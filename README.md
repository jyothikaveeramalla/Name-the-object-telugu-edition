# Name-the-object-telugu-edition
# 🏷️ Name The Object: Telugu Edition

A **crowdsourced AI-powered platform** to preserve Telugu dialects — by collecting and comparing how people across different regions name traditional household or cultural items.

---

## 🌟 Features

- 🧠 AI-generated captions using `blip-image-captioning-base`
- 🗣️ Users label objects in their **own dialect/language (Telugu supported)**
- 🤖 Compare user input with AI caption using **semantic similarity** (`paraphrase-multilingual-MiniLM-L12-v2`)
- 📤 Upload objects, add descriptions, and specify region
- 📊 View community-contributed data and dialectal diversity
- 💾 Works **offline** after initial model load — no API calls

---

## 📂 App Sections

| Page      | Purpose                                                                 |
|-----------|-------------------------------------------------------------------------|
| `identify` | View an image, add your dialect word, and compare with AI caption      |
| `upload`   | Upload new object images with region and cultural info                 |
| `view`     | Browse previously submitted objects and responses                      |

---

## 🧠 AI Models Used

1. **Image Captioning**  
   `Salesforce/blip-image-captioning-base` – Generates English caption for images

2. **Multilingual Semantic Similarity**  
   `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` – Compares Telugu input to English caption based on meaning

✅ Works across languages without translation using multilingual embeddings!

---


