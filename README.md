# SongRecommendation
A song recommendation system.

This recommendation system uses the dataset "https://www.kaggle.com/datasets/maharshipandya/-spotify-tracks-dataset" to find different artists, 
and gets the 5 most popular songs from this artist using Genius API. 

### HOW TO RUN THIS PROJECT

### 1. Start Qdrant (Vector DB)

Make sure Docker is running, then run:

```bash
docker run -d \
  --name qdrant \
  -p 6333:6333 \
  qdrant/qdrant
```
### 2. Run app_interface/backend/rec_system.py and app_interface/backend/vector_db.py

### 3. Run the system
In terminal, type:
```bash
streamlit run app_interface/app.py 
```
### And you're all done!
