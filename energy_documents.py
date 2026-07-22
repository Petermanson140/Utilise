#Importing all the necessary libraries
import requests
import os

#Creating the rag_docs folder if it doesn't exist
os.makedirs("rag_docs", exist_ok=True)

#List of UK energy guidance URLs to download for the application
web_urls = [
    {
    "url": "https://www.london.gov.uk/programmes-strategies/environment-and-climate-change/energy/energy-homes",
    "filename": "london_energy_homes.txt"
},
{
    "url": "https://www.thameswater.co.uk/help/water-saving",
    "filename": "thames_water_saving.txt"
},
{
    "url": "https://www.gov.uk/apply-great-british-insulation-scheme",
    "filename": "great_british_insulation.txt"
},
    {
        "url": "https://www.ofgem.gov.uk/check-if-energy-price-cap-affects-you",
        "filename": "ofgem_price_cap.txt"
    },
    {
        "url": "https://energysavingtrust.org.uk/hub/quick-tips-to-save-energy/",
        "filename": "energy_saving_tips.txt"
    },
    {
        "url": "https://www.gov.uk/the-warm-home-discount-scheme",
        "filename": "warm_home_discount.txt"
    },
    {
        "url": "https://www.gov.uk/energy-company-obligation",
        "filename": "eco4_scheme.txt"
    }
]

#Dataset guidance pages
dataset_urls = [
    {
        "url": "https://www.gov.uk/guidance/national-energy-efficiency-data-framework-need-guidance",
        "filename": "need_guidance.txt"
    },
    {
        "url": "https://www.gov.uk/government/statistics/energy-follow-up-survey-efus-2011",
        "filename": "efus_overview.txt"
    },
    {
        "url": "https://www.gov.uk/government/collections/english-housing-survey",
        "filename": "ehs_overview.txt"
    },
    {
        "url": "https://www.gov.uk/government/statistics/english-housing-survey-2022-to-2023-headline-report",
        "filename": "ehs_headline_report.txt"
    },
    {
        "url": "https://www.gov.uk/government/statistics/national-energy-efficiency-data-framework-need-report-2023",
        "filename": "need_report_2023.txt"
    }
]

headers = {
    "User-Agent": "Mozilla/5.0"
}

# ── Download web pages ────────────────────────────────────────────
print("Downloading web pages...")
print("=" * 50)

all_urls = web_urls + dataset_urls

for item in all_urls:
    try:
        print(f"Downloading {item['filename']}...")
        response = requests.get(item["url"], headers=headers, timeout=15)
        
        with open(f"rag_docs/{item['filename']}", "w", encoding="utf-8") as f:
            f.write(response.text)
        
        print(f"Saved {item['filename']}")
    
    except Exception as e:
        print(f"Failed {item['filename']}: {e}")

        # ── Summary ───────────────────────────────────────────────────────
print("\n" + "=" * 50)
print("All documents ready in rag_docs folder")
print(f"Total files: {len(os.listdir('rag_docs'))}")
print("\nFiles in rag_docs:")
for f in sorted(os.listdir("rag_docs")):
    size = os.path.getsize(f"rag_docs/{f}")
    print(f"  {f} ({size:,} bytes)")