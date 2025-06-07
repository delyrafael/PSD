# PSD

## Transforming movie insights into actionable sentiment trends.

![Last Commit](https://img.shields.io/github/last-commit/delyrafael/PSD?style=flat-square&color=blue&label=last%20commit)
![Jupyter Notebook](https://img.shields.io/badge/jupyter%20notebook-81.6%25-orange?style=flat-square)
![Languages](https://img.shields.io/github/languages/count/delyrafael/PSD?style=flat-square&color=green&label=languages)
![Repository Size](https://img.shields.io/github/repo-size/delyrafael/PSD?style=flat-square&color=orange)

## Built with the tools and technologies:

![JSON](https://img.shields.io/badge/JSON-000000?style=flat-square&logo=json&logoColor=white)
![Markdown](https://img.shields.io/badge/Markdown-000000?style=flat-square&logo=markdown&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![TOML](https://img.shields.io/badge/TOML-9C4221?style=flat-square&logo=toml&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=flat-square&logo=scikit-learn&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-43B02A?style=flat-square&logo=selenium&logoColor=white)

![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat-square&logo=numpy&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=flat-square&logo=plotly&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=flat-square&logo=openai&logoColor=white)

---

## Table of Contents

- [Overview](#overview)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Usage](#usage)

---

## Overview

Analisis sentimen adalah salah satu teknik dalam pemrosesan bahasa alami (NLP) yang bertujuan untuk mengidentifikasi opini atau emosi dalam teks. Dalam penelitian ini, dikembangkan sistem analisis sentimen berbasis Large Language Model (LLM) menggunakan API OpenAI, dengan fokus pada ulasan film. Tujuan dari penelitian ini adalah untuk mengembangkan sistem analisis sentimen dan summarization yang efektif, serta mengevaluasi akurasi hasilnya. Sistem ini melalui tahapan akuisisi data, eksplorasi data awal (EDA), preprocessing, dan penerapan analisis sentimen berbasis agen. Hasil dari analisis sentimen kemudian disajikan dalam bentuk ringkasan menggunakan model LLM. Model yang dibangun menunjukkan akurasi 94,10% dalam klasifikasi sentimen ulasan film, dengan distribusi sentimen yang hampir seimbang antara positif dan negatif. Ulasan positif lebih banyak menyoroti kualitas cerita dan pengalaman emosional, sementara ulasan negatif cenderung mengkritik aspek orisinalitas dan eksekusi film. Hasil ini menunjukkan efektivitas model dalam analisis sentimen dan summarization, serta memberikan wawasan yang berguna untuk peningkatan kualitas film di masa mendatang.

### Key Features
This project aims to simplify the analysis of movie reviews while enhancing user engagement. The core features include: 
- ⚡ **Interactive Dashboard**: Visualize sentiment trends and common phrases effortlessly. 
- 🎯 **Al-Powered Insights**: Utilize OpenAl for advanced sentiment analysis and summarization. 
- 🔧 **Automated Web Scraping**: Seamlessly gather data from online sources with Selenium and BeautifulSoup. 
- 🚀 **Performance Evaluation**: Assess machine learning models with detailed metrics for informed improvements. 
- 📚 **CSV Support**: Easily upload and analyze your own datasets for personalized insights.

## Getting Started

### Prerequisites

Before you begin, ensure you have the following requirements:

- **Python**: 3.7 or higher
- **Operating System**: Linux, Windows, or macOS

### Installation

#### Clone and Install Dependencies

```bash
# Clone the repository
git clone https://github.com/delyrafael/PSD.git
cd PSD

# Install PyTorch version
cd code
pip install -r requirements.txt
```

### Usage

#### Quick Inference

run the project with:
```bash
streamlit run .\dashboard.py
```
