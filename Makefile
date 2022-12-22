dev:
	docker-compose up -d

dev-down:
	docker-compose down

start-server:
	uvicorn app.main:app --reload

install-modules:
	pip install fastapi[all] fastapi-mail==1.2.2 fastapi-jwt-auth[asymmetric] passlib[bcrypt] pymongo