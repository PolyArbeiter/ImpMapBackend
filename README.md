# Impression Map Backend

This project is a Django backend providing Impression Map mobile app with RESTful API.

## How to

1. docker compose up
2. docker compose exec web python manage.py migrate --noinput
3. docker compose exec web python manage.py create_initial_data
4. send credentials to http://localhost:8000/api/v1/auth/login/ (POST)
    ```json
    {
        "username": "admin",
        "password": "admin"
    }
    ```
5. go to http://localhost:8000/api/v1/impressions/impressions/ (GET)

## Accessible endpoints

- auth
    - /api/v1/auth/ - GET (urls)
    - /api/v1/auth/login/ - POST, JSON (username=admin, password=admin)
    - /api/v1/auth/logout/ - POST
    - /api/v1/auth/register/ - POST, JSON (username, password)
- impressions
    - /api/v1/impressions/ - GET (urls)
    - /api/v1/impressions/impressions/ - GET (list)
    - /api/v1/impressions/impressions/ - POST, JSON
    - /api/v1/impressions/impressions/\<id\>/ - GET
    - /api/v1/impressions/impressions/\<id\>/ - PUT

## TODO

- [x] auth
- [x] impressions
- [x] media
- [ ] profiles
- [ ] security
- [ ] stats + admin
