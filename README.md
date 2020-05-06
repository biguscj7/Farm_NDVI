# Farm_NDVI
Project to use ESA Sentinel-2 data to compute NDVI and EVI values for a given area

---
# Main packages used
- geopandas
- rasterio
- sentinelhub
---
# Concept
Project will automate the downloading of new Sentinel-2 data and will process that data to compute EVI and NDVI metrics for a pasture section. There will be multiple outputs from the processing of this data. The first will be KML's with the index imagery embedded. Another output will be populating a database (SQLite) with data for paddocks over time. Possible follow on capabilities will be to provide graphs combining grazing patterns/rainfall and index values.

