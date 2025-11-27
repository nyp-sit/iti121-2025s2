"""Batch processing for QA embedding pairs generation using OpenAI batch API."""

import asyncio
import json
import os
import re
import tempfile
import uuid
import warnings
from typing import Any, List

from llama_index.core.schema import MetadataMode, TextNode

from llama_index.finetuning.embeddings.common import (
    DEFAULT_QA_GENERATE_PROMPT_TMPL,
    EmbeddingQAFinetuneDataset,
    load_existing_data,
)


async def generate_qa_embedding_pairs_batch(
    nodes: List[TextNode],
    openai_client: Any,  # OpenAI client
    qa_generate_prompt_tmpl: str = DEFAULT_QA_GENERATE_PROMPT_TMPL,
    num_questions_per_chunk: int = 2,
    model: str = "gpt-3.5-turbo",
    on_failure: str = "continue",  # options are "fail" or "continue"
    output_path: str = "qa_finetune_dataset.json",
    verbose: bool = True,
    poll_interval: int = 10,  # seconds between polling for batch completion
) -> EmbeddingQAFinetuneDataset:
    """
    Generate QA pairs from a set of nodes using OpenAI batch processing API.

    This function creates a batch of prompts and processes them using OpenAI's
    batch completion API, which is more efficient for large numbers of requests.

    Args:
        nodes (List[TextNode]): List of TextNode objects to process.
        openai_client: OpenAI client instance (e.g., openai.OpenAI()).
        qa_generate_prompt_tmpl (str): The template for generating QA prompts.
        num_questions_per_chunk (int): Number of questions to generate per chunk of text.
        model (str): The OpenAI model to use for batch processing. Defaults to "gpt-3.5-turbo".
        on_failure (str): Action to take on failures ('fail' or 'continue').
        output_path (str): The file path to save the JSON output.
        verbose (bool): If True, print debugging messages.
        poll_interval (int): Seconds to wait between polling for batch completion.

    Returns:
        EmbeddingQAFinetuneDataset: The generated dataset.

    """
    queries, corpus, relevant_docs = load_existing_data(output_path)

    node_dict = {
        node.node_id: node.get_content(metadata_mode=MetadataMode.NONE)
        for node in nodes
    }

    start_index = len(corpus)
    nodes_to_process = list(node_dict.items())[start_index:]

    if not nodes_to_process:
        if verbose:
            print("No new nodes to process.")
        dataset = EmbeddingQAFinetuneDataset(
            queries=queries, corpus=corpus, relevant_docs=relevant_docs
        )
        return dataset

    # Create batch of prompts
    batch_requests = []
    node_id_mapping = {}  # Map request index to node_id

    for idx, (node_id, text) in enumerate(nodes_to_process):
        prompt = qa_generate_prompt_tmpl.format(
            context_str=text, num_questions_per_chunk=num_questions_per_chunk
        )
        # Create request for chat completion API
        request = {
            "custom_id": f"request-{idx}",
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
            },
        }
        batch_requests.append(request)
        node_id_mapping[idx] = node_id
        # Also store corpus entry
        corpus[node_id] = text

    if verbose:
        print(f"Created batch with {len(batch_requests)} requests.")

    # Create temporary JSONL file for batch
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        for request in batch_requests:
            f.write(json.dumps(request) + "\n")
        batch_file_path = f.name

    try:
        # Upload batch file
        if verbose:
            print("Uploading batch file...")
        with open(batch_file_path, "rb") as f:
            batch_file = openai_client.files.create(file=f, purpose="batch")
        
        if verbose:
            print(f"Batch file uploaded: {batch_file.id}")

        # Create batch job
        if verbose:
            print("Creating batch job...")
        batch = openai_client.batches.create(
            input_file_id=batch_file.id,
            endpoint="/v1/chat/completions",
            completion_window="24h",
        )

        if verbose:
            print(f"Batch job created: {batch.id}. Status: {batch.status}")

        # Poll for completion
        while batch.status in ["validating", "in_progress", "finalizing"]:
            await asyncio.sleep(poll_interval)
            batch = openai_client.batches.retrieve(batch.id)
            if verbose:
                print(f"Batch status: {batch.status}")

        if batch.status == "failed":
            error_msg = f"Batch processing failed: {batch.errors}"
            if on_failure == "fail":
                raise RuntimeError(error_msg)
            elif on_failure == "continue":
                if verbose:
                    print(f"Warning: {error_msg}. Continuing with available results.")
        elif batch.status != "completed":
            error_msg = f"Batch processing ended with status: {batch.status}"
            if on_failure == "fail":
                raise RuntimeError(error_msg)
            elif on_failure == "continue":
                if verbose:
                    print(f"Warning: {error_msg}. Continuing with available results.")

        # Retrieve results
        if verbose:
            print("Retrieving batch results...")
        output_file_id = batch.output_file_id
        if output_file_id:
            output_file = openai_client.files.content(output_file_id)
            results_content = output_file.read().decode("utf-8")
            
            # Parse results (JSONL format)
            results = []
            for line in results_content.strip().split("\n"):
                if line:
                    results.append(json.loads(line))

            # Process results
            for result in results:
                custom_id = result.get("custom_id", "")
                # Extract request index from custom_id (format: "request-{idx}")
                try:
                    request_idx = int(custom_id.split("-")[1])
                    node_id = node_id_mapping[request_idx]
                except (IndexError, ValueError, KeyError):
                    if verbose:
                        print(f"Warning: Could not parse custom_id {custom_id}, skipping.")
                    continue

                # Check if request was successful
                if result.get("response", {}).get("status_code") == 200:
                    response_body = result.get("response", {}).get("body", {})
                    choices = response_body.get("choices", [])
                    if choices:
                        content = choices[0].get("message", {}).get("content", "")
                        result_text = content.strip().split("\n")
                        questions = [
                            re.sub(r"^\d+[\).\s]", "", question).strip()
                            for question in result_text
                        ]
                        questions = [
                            question for question in questions if len(question) > 0
                        ][:num_questions_per_chunk]

                        num_questions_generated = len(questions)
                        if num_questions_generated < num_questions_per_chunk:
                            warnings.warn(
                                f"Fewer questions generated ({num_questions_generated}) "
                                f"than requested ({num_questions_per_chunk}) for node {node_id}."
                            )

                        for question in questions:
                            question_id = str(uuid.uuid4())
                            queries[question_id] = question
                            relevant_docs[question_id] = [node_id]
                    else:
                        if verbose:
                            print(f"Warning: No choices in response for node {node_id}.")
                        if on_failure == "fail":
                            raise RuntimeError(f"No choices in response for node {node_id}.")
                else:
                    error_info = result.get("response", {}).get("body", {}).get("error", {})
                    error_msg = error_info.get("message", "Unknown error")
                    if verbose:
                        print(f"Error processing node {node_id}: {error_msg}")
                    if on_failure == "fail":
                        raise RuntimeError(f"Error processing node {node_id}: {error_msg}")

        # Save final dataset
        dataset = EmbeddingQAFinetuneDataset(
            queries=queries, corpus=corpus, relevant_docs=relevant_docs
        )
        dataset.save_json(output_path)
        if verbose:
            print("Final dataset saved.")

        return dataset

    finally:
        # Clean up temporary file
        try:
            os.unlink(batch_file_path)
        except Exception:
            pass

