sqlinit:
	initdb -D /usr/local/var/postgres/

sqlup:
	brew services start postgresql

sqldown:
	brew services stop postgresql

sqlrestart:
	brew services restart postgresql

dockerup:
	docker-compose up --force-recreate -V -d

dockerdown:
	docker-compose down

dockerbuild:
	docker-compose build