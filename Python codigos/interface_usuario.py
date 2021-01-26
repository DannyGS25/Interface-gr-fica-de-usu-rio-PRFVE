#%% Livrerias
import pandas as pd
import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import math
import numpy as np
from sklearn.cluster import KMeans
from amplpy import AMPL,DataFrame
#from sklearn.neighbors import KNeighborsClassifier
#from matplotlib.figure import Figure

#%% Opções de janela
janela=tk.Tk()                         # Criar janela
janela.title("Processamento de dados") # Adicionar titulo
janela.geometry('1400x750')            # Largura x Altura
janela.configure(background='white')   # Cor de fundo

#%% Variáveis tkinter
var=tk.StringVar(janela)
var2=tk.StringVar(janela)
var3=tk.StringVar(janela)
var4=tk.StringVar(janela)

#%% Imagem
image=tk.PhotoImage(file="fondo.gif") # Importar imagem
image=image.subsample(1,1)            # Tamanho
Label=tk.Label(image=image)           # Adicionar etiqueta
Label.pack(fill=tk.BOTH)              # Alocação

#%% Figuras
for i in range(1,5):
    exec('figura{} = plt.figure(figsize=(5,4),dpi=100)'.format(i))
    
#%% Funções

def obtenção():
    #Variáveis globais
    global dados,titulo,distan
    
    # Pegar dados do excel o dos bancos de dados de Solomon
    if var.get()=='Teste':
        titulo = pd.read_excel('teste_2.xlsx',index_col=0)
        var2.set(titulo)
    else:
        dados = pd.read_csv(dic[var.get()], header=None)
        dados = dados.drop(range(0, 6, 1),axis=0)
        titulo = dados[0].str.split(expand = True)
        titulo = titulo.rename(columns = {0: "NO", 1: "X_coord", 2 : "Y_coord", 3 : "Demand",
                                    4: "Ready_time", 5: "Due_date", 6 : "Service"})
        titulo=titulo.head(int(e_0.get()))
        var2.set(titulo)
    titulo = titulo.astype(float)
    
    # Imprimir os requerimentas da instância
    distan = pd.DataFrame(columns=['Distancia'])
    a=0
      
    for i in range(0,len(titulo)-1):
        for j in range(0,len(titulo)-1):
            if i!=j:
                x=float(titulo.iloc[i,1])-float(titulo.iloc[j,1])
                y=float(titulo.iloc[i,2])-float(titulo.iloc[j,2])
                dist=round(math.sqrt(pow(x,2)+pow(y,2)),1)
                distan.loc[a,'Distancia']=dist
        a=a+1
    print("Quantidade minima de mercadorias:",titulo['Demand'].sum())
    print("Valor minimo do SOC:",distan['Distancia'].sum())
    
    var3.set(round(titulo['Demand'].sum(),1))
    var4.set(round(distan['Distancia'].sum(),1))
    
    
def grafica_1():
    #Variáveis globais
    global X,x,y
    
    # Criação da janela
    janela_2 = tk.Tk()
    janela_2.title("Gráfico clientes")
    
    #Obtenção das coordenadas X e Y dos clientes
    X =titulo[["X_coord", "Y_coord"]]
    x = X["X_coord"].astype("float")
    y = X["Y_coord"].astype("float")
    
    # Graficar
    opções_graf(figura1,x,y,nomes[2],nomes[1],nomes[0],janela_2)

def cluster():
    # Variáveis globais
    global asinar,centroides
    
    # Chamar dados
    obtenção()

    asinar = [] # Criar uma lista para armazenar os cores dos clusters
    X =titulo[["X_coord", "Y_coord"]]
    # Calculo dos clusters
    kmeans = KMeans(n_clusters=int(e_3.get()), random_state=0).fit(X)
    labels = kmeans.predict(X)
    centroides = kmeans.cluster_centers_
    
    # Asinar os clusters
    for row in labels:
        asinar.append(cor[row])
        
def grafica_2():
    
    # Obter os clusters
    cluster()
    
    # Criação da janela
    janela_3 = tk.Tk()
    janela_3.title("Cluster")
    
    # Graficar
    opções_graf(figura2,x,y,nomes[3],nomes[1],nomes[0],janela_3)
    
def guardar_clientes():
    
    # Obter os dados
    obtenção()
    
    # Criar e escrever em um arquivo .txt
    f = filedialog.asksaveasfile(mode='w', defaultextension=".txt")
    pd.options.display.max_rows =101
    dados_arq = str(titulo) 
    f.write(dados_arq)
    f.close() 

def guardar_cluster():
    
    # Obter dados e clusters
    obtenção()
    cluster()
    
    # Criar e escrever em um arquivo .txt
    f = filedialog.asksaveasfile(mode='w', defaultextension=".txt")
    pd.options.display.max_rows =101
    tit=pd.DataFrame(titulo)
    tit['Cluster']=asinar
    dados_arq = str(tit) 
    f.write(dados_arq)
    f.close() 
    

def modelo():
    
    # Variáveis globais
    global otimo, m, n, s, capacidade_dep, capacidade_vei, SOC_max, ampl
    global velocidad_carga, demanda, servico, inicio, ultimo, custo
    global distancia, tempo, nodos, arcos
    global titulo, dados_1, graf, indices, indices_2

    # Chamar função cluster
    cluster()
    
    # Carregar parãmetros e variáveis
    ampl = AMPL()                 # Carregar objeto AMPL
    ampl.reset()                  # Reiniciar as variáveis e parâmetros
    ampl.read('modelo_PRFVE.mod')  # Carregar modelo
    m = ampl.getParameter('m')    # Número de nós
    n = ampl.getParameter('n')    # Número de veículos
    s = ampl.getParameter('s')    # Número de estações de carregamento
    M = ampl.getParameter('M')    # Número de nós
    capacidade_dep = ampl.getParameter('capacidade_dep')  # Capacidade do depósito
    capacidade_vei = ampl.getParameter('capacidade_vei')  # Capacidade veículos
    SOC_max = ampl.getParameter('SOC_max')                # SOC max bateria
    velocidad_carga = ampl.getParameter('velocidad_carga')# Velocidade de carga
    demanda = ampl.getParameter('demanda') # Demanda de mercadorias dos clientes                 
    servico = ampl.getParameter('servico') # Tempo de serviço no cliente
    inicio = ampl.getParameter('inicio')   # Inicio da janela de tempo de atendimento
    ultimo = ampl.getParameter('ultimo')   # Fim da janela de tempo de atendimento
    custo = ampl.getParameter('custo')     # Custo de transporte do nó i ao nó j
    distancia = ampl.getParameter('distancia') # Distancia do nó i ao nó j
    tempo = ampl.getParameter('tempo') # Tempo de percorrer o nó i ao nó j
    nodos = ampl.getSet('NODOS')  # Conjunto de nós         
    arcos = ampl.getSet('ARCOS')  # Conjunto de arcos
    #ar = ampl.getSet('AR')  # Conjunto de arcos
    
    # Atribuir valores
    m.setValues([int(e_0.get())+int(e_3.get())]) # Valor do número de n
    n.setValues([int(e_2.get())])                # Valor de veículos
    s.setValues([int(e_3.get())])                # Valor de estações  
    M.setValues([1246])                # Valor de estações  
    capacidade_dep.setValues([int(e_4.get())])   # Valor de capacidade
    
    # Adicionar as estações de carregamento
    for i in range(1,int(s.value())+1):
        titulo.loc[i,'X_coord'] = round(centroides[i-1,0],1)
        titulo.loc[i,'Y_coord'] = round(centroides[i-1,1],1)
        
    # Valores das capacidades de mercadorias dos veículos
    for i in range(1,capacidade_vei.numInstances()+1):
        capacidade_vei[i] = int(e_5.get())
    
    # Valores do SOC máximo das baterias dos veículos
    for i in range(1,SOC_max.numInstances()+1):
        SOC_max[i] = int(e_6.get())
    
    # Valores da velocidade da carga das baterias dos veículos
    for i in range(1,velocidad_carga.numInstances()+1):
        velocidad_carga[i] = int(e_7.get())
    
    # Valores de demanda de mercadorias dos clientes
    for i in range(1,demanda.numInstances()+1):
        if i >= demanda.numInstances()+1-s.value():
            demanda[i] = 0
        else:
            demanda[i] = int(titulo.iloc[i-1,3])
    
    # Valores de tempo de serviço nos clientes
    for i in range(1,servico.numInstances()+1):
        if i >= servico.numInstances()+1-s.value():
            servico[i] = 0
        else:
            servico[i] = int(titulo.iloc[i-1,6])
    
    # Valores do inicio da janela de tempo de atendimento
    for i in range(1,inicio.numInstances()+1):
        if i >= inicio.numInstances()+1-s.value():
            inicio[i] = 0
        else:
            inicio[i] = int(titulo.iloc[i-1,4])
    
    # Valores do fim da janela de tempo de atendimento
    for i in range(1,ultimo.numInstances()+1):
        if i >= ultimo.numInstances()+1-s.value():
            ultimo[i] = int(titulo.iloc[0,5])
        else:
            ultimo[i] = int(titulo.iloc[i-1,5])
    
    # Criar indices para os conjuntos de dados
    indices = DataFrame(index=('Index0', 'Index1'))
    for i in range(1,int(m.value())+1):
        for j in range(1,int(m.value())+1):
            if i!=j:
                indices.addRow(i,j)
    
                
    # Valores dos arcos            
    arcos.setValues(indices)
    #ar.setValues(indices_2)
    
    
    # Valores do custo, distância e tempo   
    for i in range(1,int(m.value())+1):
        for j in range(1,int(m.value())+1):
            if i!=j:
                x=float(titulo.iloc[i-1,1])-float(titulo.iloc[j-1,1])
                y=float(titulo.iloc[i-1,2])-float(titulo.iloc[j-1,2])
                dist=round(math.sqrt(pow(x,2)+pow(y,2)),1)
                distancia[i,j]=dist
                custo[i,j]=dist*3
                tempo[i,j]=dist
    
    
def optimizar_1():
    
    # Variáveis globais
    global titulo_1, instan, dados_1
    
    # Obter dados modelo
    modelo()
    
    # Opções do solver e resolver modelo
    ampl.option['solver']='cplexamp'
    ampl.option['cplex_options']='time=2000000 threads=0 nodefile=3 workfilelim=1200\
                                  mipdisplay=2 mipinterval=1000 parallelmode=-1 mipgap=0.00 '
    ampl.solve()
    
    # Expandir variáveis e restrições
    ampl.eval('expand fluxo_tiempo_est;')
    #ampl.eval('expand fluxo_tiempo_maximo;')
    #ampl.eval('display x;')
    #ampl.eval('display t;')
    
    # Obter os valores das variáveis
    otimo= ampl.getData('x') # Arcos ativos
    y= ampl.getData('y')     # Fluxo de mercadorias
    z= ampl.getData('z')     # Fluxo de estado de carga 
    t= ampl.getData('t')     # Fluxo de tempo
    w= ampl.getData('w')     # Fluxo de tempo
    
    #print(t)
    # Criação de um DataFrame para armazem de dados
    dados_1=pd.DataFrame(columns=['No_i','No_j','Veiculo','Mercadorias',
                                  'SOC','Tempo'])
    
    # Asinar dados modelo ao DataFrame
    for k in range(1,int(n.value())+1):
        print("\nVeículo",k,":")
        for i in range(0,int(otimo.getNumRows())):
            if otimo.getRowByIndex(i)[2] == k and otimo.getRowByIndex(i)[3] == 1: 
                dados_1.loc[i,'No_i']=otimo.getRowByIndex(i)[0]
                dados_1.loc[i,'No_j']=otimo.getRowByIndex(i)[1]
                dados_1.loc[i,'Veiculo']=otimo.getRowByIndex(i)[2]
                dados_1.loc[i,'Mercadorias']=y.getRowByIndex(i)[3]
                dados_1.loc[i,'SOC']=z.getRowByIndex(i)[3]
                dados_1.loc[i,'Tempo']=t.getRowByIndex(i)[3]
                
                # Imprimir no console os resultados
                print("Do nó",int(otimo.getRowByIndex(i)[0]),
                      "ao nó",int(otimo.getRowByIndex(i)[1]),
                      "transportando",int(y.getRowByIndex(i)[3]),"unidades.",
                      "O veículo saí do", int(otimo.getRowByIndex(i)[0]),
                      "com um SOC de",round(z.getRowByIndex(i)[3],1),
                      "e um tempo de",round(t.getRowByIndex(i)[3],1))
    
    # Organizar dados por veículos e quantidade de mercadorias
    titulo_1 = titulo.set_index([pd.Index(range(1,len(titulo)+1))])
    dados_1=dados_1.sort_values(['Veiculo','Mercadorias'],ascending=False)
    
    # Criação de um dicionário
    instan = {}
    
    # Asinar ao dicionário as rotas de cada veículo para graficar
    contador = 1
    for k in range(1,int(n.value())+1):
        graf = pd.DataFrame(columns=["X_coord","Y_coord"])
        instan[contador]= graf
        instan[k].loc[0,'X_coord']=titulo_1.iloc[0,1]
        instan[k].loc[0,'Y_coord']=titulo_1.iloc[0,2]
        for i in range(0,len(dados_1[dados_1["Veiculo"]==k])):
            instan[k].loc[i+1,'X_coord']=titulo_1.iloc[int(dados_1[dados_1["Veiculo"]==k].iloc[i,1])-1,1]
            instan[k].loc[i+1,'Y_coord']=titulo_1.iloc[int(dados_1[dados_1["Veiculo"]==k].iloc[i,1])-1,2]
        contador +=1
    
    # Criação de uma janela
    janela_4 = tk.Tk()
    janela_4.title("Rotas")
    
    # Graficar
    opções_graf(figura3, instan[1].X_coord.astype("float"), instan[1].Y_coord.astype("float"), nomes[4], nomes[0], nomes[1], janela_4)    
    
    # Imprimir dados para verificar o modelo
    print(dados_1)
    #print(t)
    #print(otimo)


def opções_graf(fig,var1,var2,lab,xlab,ylab,jan):
    
    # Redefinir os valores das gráficas
    fig.clear()
    
    # Gráfico dos clientes
    ax = fig.add_subplot(111)
    ax.scatter(var1,var2,label=lab,s=50, alpha=0.5) 
    ax.scatter(float(titulo.iloc[0,1]),float(titulo.iloc[0,2]),label=nomes[5], marker='s', c='red', s=80) # Graficar
    
    # Gráfico dos clusters
    if fig == figura2:
        ax.clear()
        ax.scatter(var1, var2, c=asinar, s=50, alpha=0.5)
        ax.scatter(centroides[:, 0], centroides[:, 1], label=lab, marker='D', c='green', s=80)
        ax.scatter(float(titulo.iloc[0,1]),float(titulo.iloc[0,2]),label=nomes[5], marker='s', c='red', s=80) # Graficar
    
    # Gráfico das rotas dos veículos
    if fig == figura3:
        ax.clear()
        if len(instan[1]) != 1:
            ax.scatter(titulo_1["X_coord"].astype("float"),titulo_1["Y_coord"].astype("float"),label=nomes[2],s=50, alpha=0.5) # Graficar
            ax.plot(var1,var2,label=lab,linestyle = 'dashed',marker='o') # Graficar
        for i in range(2,len(instan)+1):
            if len(instan[i]) != 1:
                ax.plot(instan[i].X_coord.astype("float"),instan[i].Y_coord.astype("float"),label='Veículo '+str(i),linestyle = 'dashed',marker='o') # Graficar
        ax.scatter(np.round(centroides[:, 0],1), np.round(centroides[:, 1],1), label=nomes[3], marker='D', c='green', s=80)
        ax.scatter(float(titulo.iloc[0,1]),float(titulo.iloc[0,2]),label=nomes[5], marker='s', c='red', s=80) # Graficar
    
    # Opções do gráfico
    ax.set_xlabel(xlab,fontsize=15) # Nome do eixo x
    ax.set_ylabel(ylab,fontsize=15) # Nome do eixo y
    ax.legend(fontsize=15)                       # Legenda
    ax.grid()                         # Legenda
    tela = FigureCanvasTkAgg(fig, master=jan)  # Criar área de desenho                        
    tela.draw()                                # Mostrar área de desenho
    tela.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES) # Alocar
    barrafer = NavigationToolbar2Tk(tela, jan) # Criar barra de ferramentas                           
    barrafer.update()                          # Atualizar
    tela.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1) # Alocar
#%% Dicionário de dados

# Dicionário de rótulos nos gráficos
nomes = {0:"Y coordenada",1:"X coordenada",2:"Clientes",
         3:"Estaçoes de carregamento",4:"Veículo 1", 5:"Depósito"}

# Dicionário de cor dos clusters
cor = ['red','cyan','orange','blue','green','violet','salmon',
       'magenta','yellow','coral','brown','pink']

vartk = [var, var2, var3, var4]

# Dicionário do banco de dados do Solomon
dic = {"Teste": 'hola',
       "C101" : 'http://people.idsia.ch/~luca/macs-vrptw/problems/c101.txt', 
       "C102": 'http://people.idsia.ch/~luca/macs-vrptw/problems/c102.txt',
       "C103": 'http://people.idsia.ch/~luca/macs-vrptw/problems/c103.txt',
       "C104": 'http://people.idsia.ch/~luca/macs-vrptw/problems/c104.txt',
       "C105" : 'http://people.idsia.ch/~luca/macs-vrptw/problems/c105.txt', 
       "C106": 'http://people.idsia.ch/~luca/macs-vrptw/problems/c106.txt',
       "C107": 'http://people.idsia.ch/~luca/macs-vrptw/problems/c107.txt',
       "C108": 'http://people.idsia.ch/~luca/macs-vrptw/problems/c108.txt',
       "C109" : 'http://people.idsia.ch/~luca/macs-vrptw/problems/c109.txt', 
       "C201": 'http://people.idsia.ch/~luca/macs-vrptw/problems/c201.txt',
       "C202": 'http://people.idsia.ch/~luca/macs-vrptw/problems/c202.txt',
       "C203": 'http://people.idsia.ch/~luca/macs-vrptw/problems/c203.txt',
       "C204" : 'http://people.idsia.ch/~luca/macs-vrptw/problems/c204.txt', 
       "C205": 'http://people.idsia.ch/~luca/macs-vrptw/problems/c205.txt',
       "C206": 'http://people.idsia.ch/~luca/macs-vrptw/problems/c206.txt',
       "C207": 'http://people.idsia.ch/~luca/macs-vrptw/problems/c207.txt',
       "C208": 'http://people.idsia.ch/~luca/macs-vrptw/problems/c208.txt',
       "R101" : 'http://people.idsia.ch/~luca/macs-vrptw/problems/r101.txt', 
       "R102": 'http://people.idsia.ch/~luca/macs-vrptw/problems/r102.txt',
       "R103": 'http://people.idsia.ch/~luca/macs-vrptw/problems/r103.txt',
       "R104": 'http://people.idsia.ch/~luca/macs-vrptw/problems/r104.txt',
       "R105" : 'http://people.idsia.ch/~luca/macs-vrptw/problems/r105.txt', 
       "R106": 'http://people.idsia.ch/~luca/macs-vrptw/problems/r106.txt',
       "R107": 'http://people.idsia.ch/~luca/macs-vrptw/problems/r107.txt',
       "R108": 'http://people.idsia.ch/~luca/macs-vrptw/problems/r108.txt',
       "R109" : 'http://people.idsia.ch/~luca/macs-vrptw/problems/r109.txt', 
       "R110": 'http://people.idsia.ch/~luca/macs-vrptw/problems/r110.txt',
       "R111": 'http://people.idsia.ch/~luca/macs-vrptw/problems/r111.txt',
       "R112": 'http://people.idsia.ch/~luca/macs-vrptw/problems/r112.txt',
       "R201" : 'http://people.idsia.ch/~luca/macs-vrptw/problems/r201.txt', 
       "R202": 'http://people.idsia.ch/~luca/macs-vrptw/problems/r202.txt',
       "R203": 'http://people.idsia.ch/~luca/macs-vrptw/problems/r203.txt',
       "R204": 'http://people.idsia.ch/~luca/macs-vrptw/problems/r204.txt',
       "R205" : 'http://people.idsia.ch/~luca/macs-vrptw/problems/r205.txt', 
       "R206": 'http://people.idsia.ch/~luca/macs-vrptw/problems/r206.txt',
       "R207": 'http://people.idsia.ch/~luca/macs-vrptw/problems/r207.txt',
       "R208": 'http://people.idsia.ch/~luca/macs-vrptw/problems/r208.txt',
       "R209" : 'http://people.idsia.ch/~luca/macs-vrptw/problems/r209.txt', 
       "R210": 'http://people.idsia.ch/~luca/macs-vrptw/problems/r210.txt',
       "R211": 'http://people.idsia.ch/~luca/macs-vrptw/problems/r211.txt',
       "RC101": 'http://people.idsia.ch/~luca/macs-vrptw/problems/rc101.txt',
       "RC102": 'http://people.idsia.ch/~luca/macs-vrptw/problems/rc102.txt',
       "RC103": 'http://people.idsia.ch/~luca/macs-vrptw/problems/rc103.txt',
       "RC104": 'http://people.idsia.ch/~luca/macs-vrptw/problems/rc104.txt',
       "RC105": 'http://people.idsia.ch/~luca/macs-vrptw/problems/rc105.txt',
       "RC106": 'http://people.idsia.ch/~luca/macs-vrptw/problems/rc106.txt',
       "RC107": 'http://people.idsia.ch/~luca/macs-vrptw/problems/rc107.txt',
       "RC108": 'http://people.idsia.ch/~luca/macs-vrptw/problems/rc108.txt',
       "RC201": 'http://people.idsia.ch/~luca/macs-vrptw/problems/rc201.txt',
       "RC202": 'http://people.idsia.ch/~luca/macs-vrptw/problems/rc202.txt',
       "RC203": 'http://people.idsia.ch/~luca/macs-vrptw/problems/rc203.txt',
       "RC204": 'http://people.idsia.ch/~luca/macs-vrptw/problems/rc204.txt',
       "RC205": 'http://people.idsia.ch/~luca/macs-vrptw/problems/rc205.txt',
       "RC206": 'http://people.idsia.ch/~luca/macs-vrptw/problems/rc206.txt',
       "RC207": 'http://people.idsia.ch/~luca/macs-vrptw/problems/rc207.txt',
       "RC208": 'http://people.idsia.ch/~luca/macs-vrptw/problems/rc208.txt'}


# Dicionário de rótulos para o menú
instancias=['Teste','C101','C102','C103','C104','C103','C104','C105','C106',
          'C107','C108','C109','C201','C202','C203','C204','C205',
          'C206','C207','C208','R101','R102','R103','R104','R105',
          'R106','R107','R108','R109','R110','R111','R112','R201',
          'R202','R203','R204','R205','R206','R207','R208','R209',
          'R210','R211','RC101','RC102','RC103','RC104','RC105',
          'RC106','RC107','RC108','RC201','RC202','RC203','RC204','RC205',
          'RC206','RC207','RC208']

# Dicionário de rótulos na interface
rotulos = {0:"Interface gráfica do usuário para veículos elétricos:",
           1:"Escolha uma instância", 2: "Número de dados",
           3:"Número de clusters", 4: "Gráficar", 5: "Salvar",
           6:"N° de veículos", 7: "N° estações de carregamento", 
           8:"Capacidade do depósito",9:"Capacidade dos veículos", 
           10:"SOC max dos veículos",11:"Velocidad de carregamento", 
           12: "Otimização N°1", 13: "Otimização N°2",14:"Min. Mercadorias:",
           15: "Min. SOC:"}

# Dicionário para estilos de fontes
fontes = {0: "Helvetica 20 bold", 1: "Helvetica 10 bold"}

# Dicionário para executar funções
executar = {0: obtenção, 1: grafica_1, 2: grafica_2,
            3: guardar_clientes, 4: guardar_cluster,
            5:optimizar_1}

# Dicionário de rótulos dos botões
botões = {0: "Carregar dados", 1: "Gráfico dos clientes",
          2: "Gráfico das zonas", 3: "Dados clientes", 
          4: "Dados clusters",5: "Rodar"}

#%% Rótulos
for t in range(0,16,1):
    if t == 0:
        exec('r_{} = tk.Label(janela,text=rotulos[t],font=fontes[0],bg="white",fg="black")'.format(t))
        exec('r_{}.pack(padx=5,pady=5,ipadx=5,ipady=5)'.format(t))
    if t > 0 and t<3:
        exec('r_{} = tk.Label(janela,text=rotulos[t],font=fontes[1],bg="white",fg="black")'.format(t))
        exec('r_{}.pack(padx=5,pady=5,ipadx=5,ipady=5)'.format(t))
        exec('r_{}.place(x=430, y=80*t-10)'.format(t))
    if t>=4 and t<=5:
        exec('r_{} = tk.Label(janela,text=rotulos[t],font=fontes[1],bg="white",fg="black")'.format(t))
        exec('r_{}.pack(padx=5,pady=5,ipadx=5,ipady=5)'.format(t))
        exec('r_{}.place(x=430, y=80*t+40)'.format(t))
    if t > 5 and t<12:
        exec('r_{} = tk.Label(janela,text=rotulos[t],font=fontes[1],bg="white",fg="black")'.format(t))
        exec('r_{}.pack(padx=5,pady=5,ipadx=5,ipady=5)'.format(t))
        exec('r_{}.place(x=760, y=80*t-410)'.format(t))
    if t >= 12 and t<14:
        exec('r_{} = tk.Label(janela,text=rotulos[t],font=fontes[1],bg="white",fg="black")'.format(t))
        exec('r_{}.pack(padx=5,pady=5,ipadx=5,ipady=5)'.format(t))
        exec('r_{}.place(x=1100, y=80*t-890)'.format(t))
    if t >= 14:
        exec('r_{} = tk.Label(janela,text=rotulos[t],font=fontes[1],bg="white",fg="black")'.format(t))
        exec('r_{}.pack(padx=5,pady=5,ipadx=5,ipady=5)'.format(t))
        exec('r_{}.place(x=430, y=20*t)'.format(t))


#%% Entradas   
for t in range(0,8,1): 
    if t == 0:
        exec('e_{} = tk.Entry(janela,width=28,bg="snow3")'.format(t))
        exec('e_{}.pack(padx=5,pady=5,ipadx=5,ipady=5)'.format(t))
        exec('e_{}.config(justify="center")'.format(t))
        exec('e_{}.place(x=430, y=80*t+180)'.format(t))
    if t>=2:
        exec('e_{} = tk.Entry(janela,width=28,bg="snow3")'.format(t))
        exec('e_{}.pack(padx=5,pady=5,ipadx=5,ipady=5)'.format(t))
        exec('e_{}.config(justify="center")'.format(t))
        exec('e_{}.place(x=760, y=80*t-65)'.format(t))
        
#%% Menú
var.set('Selecionar')
opção=tk.OptionMenu(janela, var,*instancias)
opção.config(width=22)
opção.pack(side=tk.TOP,padx=5,pady=5)
opção.place(x=430, y=90)

#%% Botões

for t in range(0,6,1):
    if t == 0:
        exec('b_{} = tk.Button(janela,text=botões[t],fg="black",command=executar[t],width=24)'.format(t))
        exec('b_{}.pack(padx=5,pady=5,ipadx=5,ipady=5)'.format(t))
        exec('b_{}.place(x=430, y=25*t+210)'.format(t))
    if t>0 and t<3:
        exec('b_{} = tk.Button(janela,text=botões[t],fg="black",command=executar[t],width=24)'.format(t))
        exec('b_{}.pack(padx=5,pady=5,ipadx=5,ipady=5)'.format(t))
        exec('b_{}.place(x=430, y=25*t+355)'.format(t))
    if t>=3 and t<5:
        exec('b_{} = tk.Button(janela,text=botões[t],fg="black",command=executar[t],width=24)'.format(t))
        exec('b_{}.pack(padx=5,pady=5,ipadx=5,ipady=5)'.format(t))
        exec('b_{}.place(x=430, y=25*t+385)'.format(t))
    if t>=5:
        exec('b_{} = tk.Button(janela,text=botões[t],fg="black",command=executar[t],width=24)'.format(t))
        exec('b_{}.pack(padx=5,pady=5,ipadx=5,ipady=5)'.format(t))
        exec('b_{}.place(x=1100, y=20*t)'.format(t))

#%% Etiquetas

for t in range(0,2,1):
        exec('et_{} = tk.Label(janela,textvariable=vartk[t+2],font=fontes[1],bg="snow3",fg="black",width=5)'.format(t))
        exec('et_{}.pack(padx=5,pady=5,ipadx=5,ipady=5)'.format(t))
        exec('et_{}.place(x=560, y=25*t+280)'.format(t))

janela.mainloop()