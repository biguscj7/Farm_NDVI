# Sentinel project

## Outputs
- Database
- KMZ
- Current ‘best’ paddock
- Visualization of health over time

## Inputs
- KMLs
	- Pad max extents by _ amount
	- Check for holes
	- Verify CRS
- Sentinel imagery
	- Check last ingest
	- Request via api for more recent data
	- Download imagery to correct folder and unpack if needed
	- Ensure extents of query are covered
- User classification of imagery
	- Show TCI
	- Request if area is visible
	- Request if visible moisture is present
- Cow paddock move info

>## Processing
>	- Cut imagery to max extent
>	- Compute index based on bands
>	- Create colored index visuals
>	- Create true color image
>		- Consider buffering this for cloud view
>	- Query user for cloud data
>	- Pull NCDC data for rain and temp

>## Classes
>	- Imagery pass
>		- Instantiate with info for folder and max extents for clipping
>		- Methods to generate indices geotiffs
>		- Method to generate TCI geotiff? PNG 
>	- KML info
>		- Instantiate with file info
>		- Provide method for max extents
>		- Provide method to transform into new crs 
>	- SQLAlchemy for SQLite
