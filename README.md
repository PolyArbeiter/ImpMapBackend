# Impression Map Backend

This project is a Django backend providing Impression Map mobile app with RESTful API.

## Accessible endpoints

- auth
    - /api/v1/auth/ - GET (urls)
    - /api/v1/auth/login/ - POST, JSON (username=user, password=0)
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
- [ ] media
- [ ] profiles
- [ ] security
- [ ] stats + admin
