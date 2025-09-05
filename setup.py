from setuptools import setup, find_packages

setup(
    name="fx_transactions_tools",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fpdf==1.7.2",
        "pdfplumber==0.10.3",
        "clickhouse-driver==0.2.6",
        "pandas==2.2.2"
    ],
    entry_points={
        "console_scripts": [
            # You must add a main() function to these scripts for this to work
            "fx-generate=generate_fx_transactions_pdf:main",
            "fx-extract=pdf_to_csv_fx_transactions:main",
            "fx-enrich=fx_transactions_with_rates:main"
        ]
    },
    include_package_data=True,
    description="FX Transactions PDF/CSV Utility",
    author="Your Name",
)

