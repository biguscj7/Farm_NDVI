# Farm_NDVI
Project to use ESA Sentinel-2 data to inform rotational grazing decisions using remote sensing

---
# Main packages used
- geopandas
- pandas
- rasterio
- sentinelhub
---
# Concept
Project will automate the downloading of new Sentinel-2 data and will process that data to compute metrics for each pasture section. The goal is to provide a reliable and useful input to decisions on which paddocks to graze and how long to leave the herd on each paddock. 

# Outputs
## KMZ's
Produces KMZs that display index data as a Google Earth overlay with a color map to enable visualizing paddock status.

## CSV stat files
Each satellite pass's data is written to a file in csv format for later processing

## Data visualizations
Graphs / charts and other non-imagery based products to enable assessment.

## Database
In work

## Thoughts for continued work
- Part way through implementing environment variables for data storage on DigitalOcean droplet
- Implement 'additive' classification of clouds rather than re-doing the whole thing
- Graph info from sentinelapi query for date & clouds
- Automate download/unzip/processing of files
- Decide on what data to retain

## Completed updates
- Implement processing on the c440 machine
- Update the c440 machine to Ubuntu 20

