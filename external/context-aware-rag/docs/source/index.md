<!--
SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0
 *
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
 *
http://www.apache.org/licenses/LICENSE-2.0
 *
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->


# NVIDIA VSS Context RAG (vss-ctx-rag)

vss-ctx-rag is a flexible library designed to seamlessly integrate into existing data processing workflows to build customized RAG pipelines.

## Key Features

- [**Data Ingestion Service:**](./overview/features.md#ingestion-strategies) Add data to the RAG pipeline from a variety of sources.
- [**Data Retrieval Service:**](./overview/features.md#retrieval-strategies) Retrieve data from the RAG pipeline using natural language queries.
- [**Function and Tool Components:**](./overview/architecture.md#components) Easy to create custom functions and tools to support your existing workflows.
- [**Swappable Databases:**](./overview/architecture.md#) Use a variety of databases to store and retrieve data.
- [**GraphRAG Support:**](./overview/architecture.md#) Seamlessly extract knowledge graphs from data to support your existing workflows.
- [**Observability:**](./overview/features.md#otel-and-metrics) Monitor and troubleshoot your workflows with any OpenTelemetry-compatible monitoring tool.


With vss-ctx-rag, you can quickly build RAG pipelines to support your existing workflows.

## Links

 * [Documentation](./index.md): Explore the full documentation for vss-ctx-rag.
 * [vss-ctx-rag Architecture](./overview/architecture.md): Learn more about how vss-ctx-rag works and its components.
 * [Getting Started Guide](./guides/index.md): Set up your environment and start integrating vss-ctx-rag into your workflows.
 * [Examples](./guides/library.md#document-ingestion): Explore examples of vss-ctx-rag workflows.
 * [Troubleshooting](./troubleshooting.md): Get help with common issues.
 * [Release Notes](./release-notes.md): Learn about the latest features and improvements.


## Table of Contents

```{toctree}
:maxdepth: 2

Introduction <./intro/index.md>
Getting Started <./guides/index.md>
Overview <./overview/index.md>
Troubleshooting <./troubleshooting.md>
Release Notes <./release-notes.md>
Code of Conduct <./code-of-conduct.md>
Contributing <./contributing.md>
```
