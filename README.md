# Face Verification using Rest Framework Djanggo
Face recognition model using VGG-Face, backend detector using MTCNN, and distance matrix using cosine similarity.
- Python 3.9.0
- Djanggo 3.2.18
- Djanggo REST Framework 3.12.4
- DeepFace 0.0.75
  
# Usage
### API EndPoints
Upload Images
```
POST: /api/verif/
```
### Request:
```
Content-Type: multipart/form-data
```
### Body:
| Key | Type | Description |
|----------|----------|----------|
| `image1` | `file` | `The first image` |
| `image2` | `file` | `The second image` |

### Example using curl:
```
curl -X POST http://localhost:8000/api/verif/ \
  -F "image1=@path/to/your/image1.jpg" \
  -F "image2=@path/to/your/image2.jpg"
```

### Response:
```
{
    "verified": true,
    "distance": 0.5343668325688979
}
```
