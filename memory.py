# algoritmos de gerencia de espaco livre

# o controle de espaco livre tem que ser feito com lista ligada: ver aula15.pdf
# Nao vai dar pra usar o bitmap
from struct import pack,unpack
from linkedlist import *
from paging import *


class Memory:
    def __init__ (self, total, s, p, filename):
        self.tamanho = total
        self.s = s
        self.p = p
        self.arquivo = filename
        self.tabela = []
        
        #monta a tabela de paginas para esta memoria
        self.set_tabela()
        
        #lista que vai espelhar a situacao da memoria. Vamos escrever essa lista no arquivo
        self.vetor = [-1] * self.tamanho 
        
        #lista ligada para controle do espaco livre da memoria
        self.lista = LinkedList('L',0,self.tamanho,None)
        
        
        #Abre o arquivo para a memoria
        self.memfile = open (filename,'wb')
        
        #define tamanho do arquivo binario em bytes
        # b signed char => 1 byte
        self.memfile.write(pack(str(self.tamanho)+'b',*self.vetor))
        self.memfile.flush()

    def __del__ (self):
        self.memfile.close()
    
    # escreve data (inteiro) na posicao position da memoria
    def writebin (self,position,data):
        self.memfile.seek(position);
        bindata = pack('1b',data)
        self.memfile.write(bindata)
        self.memfile.flush()
    
    # atualiza memoria escrevendo pid nos espacos ocupados e -1 nos livres
    def set_update(self,inicio,pid,qtde,reservado):
        for i in range(qtde):
            self.writebin(inicio + i,pid)
            self.vetor[int(inicio) + i] = int(pid)
        i += 1
        while i < reservado:
            self.writebin(inicio + i,-1)
            self.vetor[int(inicio) + i] = -1
            i +=1
            
    def get_lista(self):
        return self.lista
        
    #retorna o tamanho de pagina    
    def get_p(self):
        return self.p
        
    #retorna o tamanho da memoria    
    def get_tamanho(self):
        return self.tamanho
        
    #monta a tabela de paginas da memoria
    def set_tabela(self):
        npag = int(self.tamanho/self.p)
        j = 0
        p = int(self.p)
        for i in range(npag):
            pagina = Page(j,p)
            self.tabela.append(pagina)
            j += p
            
    #mostra a tabela de paginas da memoria     
    def show_tabela(self):
        j = 0
        for pag in self.tabela:
            print 'pagina num: ' + str(j) +' com o processo de id:' + str(pag.procId) + ' presente/ausente: ' + str(pag.presente) + ' mapeada: ' + str(pag.mapeada) + ' tAcesso: ' + str(pag.tAcesso)
            j+=1
    
    # ->>>>> APENAS PARA A MEMORIA VIRTUAL        
    #quando um processo chega ele eh carregado na tabela de paginas da mem virtual
    def get_pagina(self,proc):
        #pega o num de paginas que o processo vai utilizar
        numPag = int(proc.get_reserva()/self.p)
        base = proc.get_base()
        pid = proc.get_pid()
        
        #k determina a primeira pagina a ser marcada
        k = base/self.p
        for i in range(numPag):
            self.tabela[k+i].procId = pid
            
        

    # le a posicao pos do arquivo de memoria e devolve seu conteudo
    def readbin (self, pos):
        fin = open(self.arquivo,"rb")
        fin.seek(pos)
        x = int(unpack('1b',fin.read(1))[0])
        fin.close()
        return x
    
    # remove pid da memoria e coloca -1
    def removebin(self, data):
        for i in range(self.tamanho):
            x = self.readbin(i)
            if data == x:
                self.writebin (i,-1)
    
    # imprime o conteudo de todo o arquivo de memoria
    def dump (self):
        print "[Posicao| PID]"
        for i in range(self.tamanho):
            #print('Posicao ' + str(i) + ' PID: ' +str(self.readbin(i)))
            print('[' + str(i) + ' | ' +str(self.readbin(i))+']'), 

    #BEST FIT
    #varre a lista ligada e procura o MENOR espaco vazio para alocar o processo
    def best_fit(self,p):
       return self.search_fit(p,1)

    #WORST FIT
    #varre a lista ligada e procura o MAIOR espaco vazio para alocar o processo
    def worst_fit(self,p):
        return self.search_fit(p,2)
     
    def search_fit(self,p,metodo):

        if metodo == 1:
            print 'Best Fit'
        else:
            print 'Worst Fit'
        
        #obtem a lista ligada da memoria
        lista = self.lista
        
        #->>>Parte 1: encontra um espaco livre na lista ligada para o processo que chega
         
        #verfica o espaco ocupado pelo processo p
        ocupa = p.get_ocupa()
        reserva = p.get_reserva()
        
        #cria os elementos que varrem a lista
        current = lista.get_head()
        posicao = None

        #varre a lista e pega a maior ou menor posicao de tamanho livre que caiba o processo e coloca em 'posicao'
        while current:
			# se tem espaco livre e cabe o processo (usando tamanho da pagina)
            if current.get_data() == 'L' and current.get_tamanho() >= reserva:
                if posicao == None:
                    posicao = current
                else:
                    #se se trata do best fit
                    if metodo == 1:
                        if current.get_tamanho() < posicao.get_tamanho():
                            posicao = current
                    #se se trata do worst fit
                    else:
                        if current.get_tamanho() > posicao.get_tamanho():
                            posicao = current
                            
            current = current.get_next()
         
        #pega onde a posicao escolhida se inicia e o qual eh o tamanho
        ini = posicao.get_inicio()
        tam = posicao.get_tamanho()
        
        #caso a posicao encontrada seja do tamanho exato requerido (levando em consideracao o tam da pagina)
        if (tam == reserva):
            posicao.set_data('P')
            
        #Caso a posicao encontrada seja maior do que o suficiente
        else:

            #aloca um novo node para o processo que chega
            no = Node('P',ini,reserva,posicao)

            #o no alterado tem um novo inicio e um novo tamanho	    
            posicao.set_inicio(int(ini + reserva))
            posicao.set_tamanho(int(tam - reserva))
            
            #colocar o novo noh no lugar correto
            #caso o node alterado seja o primeiro da lista ligada
            if lista.get_head() == posicao:
                lista.set_head(no)
                posicao.set_previous(no)

            #caso seja necessario alterar qualquer outro ponto da lista
            else:
                posicao.get_previous().set_next(no)
                no.set_previous(posicao.get_previous())
                posicao.set_previous(no)

        #->>>Parte 2: Define base e limite para o processo alocado
        p.set_base(ini)
        p.set_limite(ini+reserva-1)
            
        #->>>Parte 3: Altera o vetor da memoria de acordo com o espaco destinado ao novo processo
        pid = p.get_pid()
        self.set_update(ini,pid,ocupa,reserva)

    #Recebe uma lista com os tamanhos dos processos e prepara o quick fit
    def prepare_quick_fit(self, tamanhos):
        requisitados = []
        
        #Pega quantas vezes cada elemento ocorre
        for i in len(tamanhos):
            x = tamanhos[i]
            #monta uma lista de duplas ('num de ocorrencias de X','X')
            requisitados.append(tamanhos.count(x),x)
            
        #Ordena essa lista de (num ocorrencias X, X)
        selecionados = sorted(requisitados,key=itemgetter(0));
        
        #remover os repetidos
        
        
        #pegar as 3 maiores reccorencias e montar as listas ligadas
        
        #unir as listas em uma outra lista
        
        
    def quick_fit(self, p):
        #tamanhos mais requisitados serao multiplos de s
        print 'quick fit'
        
        requisitados =[] 
        nlistas = []
        tam = self.s
        requisitados = [2*tam, 3*tam, 4*tam]
        # cria 3 listas com os itervalos mais requisitados
        for i in range(3):
            posi = 0
            posf = requisitados[i]
            nlistas.append(LinkedList('L',posi,posf,None))
            while posf < sel.tamanho:
                posi = posf+1
                posf = posf+requisitados[i]
                nlistas[i].insert('L',posi,posf)

    # compacta a memoria
    def compactar(self):
        print 'compactando memoria'
        mem = self.memfile
        k = 0;
        for i in range(self.tamanho):
            x = readbin(mem,i)
            if (x != -1):
                writebin(self.memfile,k,x)
                k += 1
        while k < self.tamanho:
            writebin(self.memfile,k,-1)
            k += 1
        self.memfile.flush()
        mem.close()

def remover_processo():
    print 'remove processo da memoria'
