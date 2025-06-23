# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

A collection of code experiments and data explorations to scratch various analytical curiosities. Each sub-project focuses on specific data analysis topics and maintains its own dependencies and documentation.

## Structure

Projects are organized as independent sub-directories, each with their own README.md, dependencies, and setup instructions. All projects use **uv** as the Python package manager.

### Current Projects

- **northern-city-map/**: Geographic data analysis of global cities using GeoNames dataset
- **daylight-visualization/**: Interactive Streamlit app for visualizing daylight duration patterns globally

## Common Commands

Navigate to individual project directories and use:
- `uv sync` - Install dependencies
- `uv run pytest` - Run tests (if available)
- `uv run streamlit run app.py` - Run Streamlit apps

## Development Preferences

- Use Python for all projects and ONLY use the uv project manager for deps