# Securitatea Informatiei, tema 1
## Iacobescu Tudor (3A6)

## Mediu de lucru utilizat
Limbaj: Python 3.8
IDE: Pycharm Professional
Librarie: PyCryptodome

## Modalitate de demonstratie
- se porneste scriptul `key_manager.py` (nodul KM)
- se pornesc 2 instante ale `client.py` (nodurile A, B)
- in una din instante, se selecteaza modul `[W]ait` (nodul B)
- in cealalta, se selecteaza modul `[I]nitiate` (nodul A)
- se urmeaza instructiunile de pe ecran pentru continuarea demonstratiei

## Modul de functionare al demonstratiei
Nodul B va astepta sa fie apelat de catre A.

Nodul A va decide, prin interfata in linia de comanda, modul de criptare al comunicarii (ECB sau OFB).
Apoi, clientul A va deschide o cale de comunicare cu KM, si ii va trimite modul de criptare. KM ii va
raspunde cu cheia corespondenta (K1/K2), criptata in mod ECB cu cheia K3. A va decripta cheia, si va
deschide o cale de comunicare cu nodul B.

Nodul B va primi modul de criptare de la A, si il va trimite la KM pentru a primi si el cheia. Nodul
A va primi de la tastatura un mesaj pentru B, il va cripta, si il va trimite. Apoi, nodul B va primi
de la tastatura un mesaj pentru A, il va cripta, si il va trimite. Clientul nodului B se va inchide
dupa transmiterea raspunsului catre A, iar A se va inchide la primirea raspunsului de la B.

## Detalii de implementare
Comunicarea intre noduri se face folosind socket-uri TCP, pe `localhost`, pe porturile `3001` (KM),
`3002` (A) si `3003` (B). Cateva functii utilitare pentru acest lucru, pentru a ne ajuta sa utilizam
un protocol simplu de comunicare (un header de 4B cu lungimea mesajului, urmat de mesaj), sunt
prezente in modulul `socket_util.py`.

Criptarea mesajelor se face folosind clasele CipherECB si CipherOFB, definite in `crypt.py`. 
CipherECB este un block cipher (folosind padare cu 0x00) iar CipherOFB este un stream cipher (care
are nevoie de un bloc IV de 16B, folosit in generarea blocurilor de keystream, si nu necesita
padare). Ambele clase folosesc la baza AES (din libraria `PyCryptodome`) instantiat pe modul ECB;
nu e posibil sa instantiem AES fara un mod, dar folosind modul ECB pe un singur bloc de 16B putem 
avea exact acelasi lucru ca si AES la baza.

In cazul in care se foloseste criptarea OFB, la initierea conversatiei nodul A genereaza si trimite
si doi vectori de initializare folositi la comunicare (unul pentru fiecare directie). Fiecare IV,
impreuna cu cheia conversatiei (obtinuta de la KM), sunt folositi pentru instantierea clasei 
CipherOFB.

## Teste efectuate
- trimiterea de mesaje scurte intre A/B cu modul ECB ('hello', 'hi')
- trimiterea de mesaje scurte intre A/B cu modul OFB
- trimiterea unui mesaj lung cu ECB (ultimul paragraf al sectiunii precedente)
- trimiterea unui mesaj lung cu OFB
