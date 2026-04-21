# 📊 Customer Behavior Analysis 

A data analysis project focused on understanding customer behavior using RFM segmentation, cohort retention analysis, and revenue trends. This project combines Python-based data processing with an interactive web dashboard for visualization.

---

## 🚀 Overview

This project analyzes customer transaction data to uncover insights such as:

* Customer segmentation using **RFM (Recency, Frequency, Monetary)**
* Monthly **revenue trends**
* **Cohort retention analysis**
* Customer lifecycle insights (loyal, at risk, lost, etc.)

The results are visualized in a modern dashboard built with **Tailwind CSS** and **Chart.js**.

---

## 🛠️ Tech Stack

### Data Analysis (Python)

* pandas
* numpy
* matplotlib
* seaborn

### Visualization (Frontend)

* HTML
* Tailwind CSS
* Chart.js

---

## 📁 Project Structure

```
customer-behavior-analysis/
├── index.html                # Main dashboard
├── css/
│   └── project2.css
├── js/
│   └── project2.js
│
├── dataset_raw/
│   └── ecommerce_raw.csv     # Raw dataset
│
├── dataset_clean/
│   └── ecommerce_clean.csv   # Cleaned dataset
│
├── python_analysis/
│   └── data_analysis.py      # Data analysis script
│   
├── output/
│   └── rfm_result.csv        # RFM segmentation results
│
└── assets/
    └── shortcut.png
```

---

## 🧹 Data Cleaning Process

The dataset was processed using a Python script that:

* Removed duplicate records
* Handled rows with null dates
* Filtered out negative quantities
* Cleaned invalid product names
* Generated a new **revenue column**

✅ Final output: **4,312 clean transactions**

---

## 📈 Key Features

### 1. RFM Segmentation

Customers are grouped into segments such as:

* Champions
* Loyal Customers
* Potential Loyalists
* At Risk
* Lost Customers

### 2. Revenue Analysis

* Monthly revenue trends (2023–2024)
* Average monetary value per segment

### 3. Cohort Retention

* Heatmap showing customer retention over time

### 4. Interactive Dashboard

* Built using Tailwind CSS
* Responsive design
* Dynamic charts powered by Chart.js

---

## ⚙️ Installation & Setup

### 1. Clone Repository

```bash
git clone https://github.com/ilhamhafizt/Customer-Behavior-Analysis
cd customer-behavior-analysis
```

### 2. Install Python Dependencies

```bash
pip install pandas numpy matplotlib seaborn
```

### 3. Run Analysis Script

```bash
python python_analysis/customer_analysis.py
```

### 4. Open Dashboard

Simply open `index.html` in your browser.

---

## 📊 Dashboard Preview

The dashboard includes:

* KPI metrics
* RFM distribution charts
* Revenue trends
* Cohort retention heatmap
* Segment summary table

---

## 🎯 Purpose

This project demonstrates:

* End-to-end data analysis workflow
* Data cleaning & transformation
* Business insight generation
* Data visualization in web format

---

## 👨‍💻 Author

**Ilham Hafizt**

* 🌐 Portfolio: https://ilhamhafizt.github.io/Portfolio-Data-Analyst/
* 💼 GitHub: https://github.com/ilhamhafizt

---
