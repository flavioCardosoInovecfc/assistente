@echo off

cd C:\
ECHO "Iniciando seu Assistente Inove"


If exist "C:\assistente" (
	
    xcopy /e /h /d /y C:\assistente\dist\assistente\*.db C:\tempassistente\
	rmdir /S/Q C:\assistente
	git clone https://github.com/flavioCardosoInovecfc/assistente.git
	xcopy /e /h /d /y C:\tempassistente\*.db C:\assistente\dist\assistente\
	rmdir /S/Q C:\tempassistente 
)

If NOT exist "C:\assistente" (
	
	git clone https://github.com/flavioCardosoInovecfc/assistente.git
	
	
)

cd c:\assistente\dist\assistente
start assistente.exe


