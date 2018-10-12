# rc-ist

# Redes de Computadores

## Este projeto foi desenvolvido por:

	Grupo 1:
	- Ana Santo, nº 79758
	- Diogo Eusebio, nº 87650
	- Joao Nuno Pedro, nº 85320

Para correr cada um dos programas não é necessário compilar, apenas correr cada um deles da seguinte forma

# Como correr:

### 	Central server:

Para correr o CS :

```
python centralserver.py -p CSport
```
TODO: IF YOU WANT TO EXPLAIN DELETE HERE

###		Backupserver Server:

Para correr o BS:

```
python3 backupserver.py -b BSport -n CSname -p CSport
```
TODO: IF YOU WANT TO EXPLAIN DELETE HERE

### 	User App:

Para correr a aplicação utilizador:

```
python userApp.py -n CSname -p CSport
```
file user.py:
	execute command: in python 2.7, 'python user.py -n CSname -p CSport'
	everything in this file works (as of 11/10/2018) on tejo server,
		tho there is a minor bug with login and logout commands,
	 	where the user can't execute a new login command unless it
		executes a logout command, which in turn says that the login
		was already closed. There is also a (very slim) chance that a strange 
		ordering of this types of commands can cause the rest of the 
		commands to ill-function on the connection instruction, cause unknown

Nota: Os parâmetros -p, -n ou -b são opcionais.
