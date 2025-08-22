# Property Summary Report Generator

A Flask web app that scrapes assessor data for King, Kitsap, and Pierce counties and generates Word reports for parcels.

## Features
- Input parcel numbers and county assessor URL
- Scrapes parcel data: site address, taxpayer name, legal description, exemptions, land acres, and related parcels
- Generates Word report with hyperlinks to parcel summaries
- Supports multiple parcels at once
- Clean front-end preview of parcel data

## Setup

1. Clone the repo:

```bash
git clone https://github.com/gonzalezbe95/parcel-report-generator.git
cd parcel-report-generator
