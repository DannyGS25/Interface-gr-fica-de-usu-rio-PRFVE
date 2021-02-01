##################################################################
#Conjuntos
param m;                                # Número de nós
param n; 								# Número de veículos
param s;								# Número de estações de carregamento
set NODOS= 1..m; 						# Conjunto de nós
set ARCOS within (NODOS cross NODOS);   # Conjunto de arcos
set CLIENTES= 2..m-s;                   # Conjunto de clientes
set VEICULOS= 1..n;                     # Conjunto de veículos
set ESTACOES= m-s+1..m;				    # Conjunto de estações de carregamento
set DUC= NODOS diff ESTACOES;			# DEPÓSITO U CLIENTES
set CUE=CLIENTES union ESTACOES; 		# CLIENTES U ESTACOES	

##################################################################
#Parâmetros
param custo {ARCOS}>=0;                 # Custo de transporte para cada arco ($USD)
param demanda {NODOS};                  # Demanda de mercadorias do cada cliente (Unidades)
param capacidade_dep;                   # Capacidade de mercadorias do depósito (Unidades)
param capacidade_vei{VEICULOS};         # Capacidade de mercadorias do veículo (Unidades)
param SOC_max{VEICULOS};				# SOC da bateria dos veículos (km)
param distancia {ARCOS}>=0;				# Distância entre os nós (km)
param tempo {ARCOS}>=0;				    # Tempo entre os nós (min) 
param servico {NODOS};			        # Tempo de servico no cliente j (min)
param velocidad_carga {VEICULOS};	    # Velocidade de carga do veículo k (min)
param inicio {NODOS};					# Tempo de inicio de tempo para o cliente j (min)
param ultimo {NODOS};					# Tempo de serviço no cliente i (min)
param M;								# Tempo maximo de carregamento (min)
param consumo {VEICULOS};				# Consumo de energia por quilômetro percorrido 
param alpha;							# Limite superior do estado de carga da bateria 
param beta;								# Limite inferior do estado de carga da bateria

##################################################################
# Variáveis
var x {(i,j) in ARCOS, k in VEICULOS} binary;         # Arco ativo (binario)
var y {(i,j) in ARCOS, k in VEICULOS} >=0;            # Fluxo de mercadorias (continuo)
var z {(i,j) in ARCOS, k in VEICULOS} >=0;            # SOC dos veiculos (continuo)
var t {(i,j) in ARCOS, k in VEICULOS} >=0;            # Tempo (continuo)
var w {j in ESTACOES, k in VEICULOS} >=0;

#################################################################
#Função objetivo
minimize custo_transporte:
	sum{k in VEICULOS,(i,j) in ARCOS} custo[i,j] * x[i,j,k]; 

minimize distancia_transporte:
	sum{k in VEICULOS,(i,j) in ARCOS} distancia[i,j] * x[i,j,k]; 

minimize tempo_transporte:
	sum{k in VEICULOS,(i,j) in ARCOS} tempo[i,j] * x[i,j,k]; 
#################################################################
#Restrições com os arcos

subject to arcos_saida {j in CLIENTES}: 
	sum{k in VEICULOS, (i,j) in ARCOS} x[i,j,k] =1;

subject to arcos_saida_2 {j in ESTACOES}: 
	sum{k in VEICULOS, (i,j) in ARCOS} x[i,j,k] <=1;
	
subject to arcos_saida_3 {k in VEICULOS}: 
	sum{(1,j) in ARCOS} x[1,j,k] <=1;

subject to dim_difer {(i,j) in ARCOS}: 
	sum{k in VEICULOS} x[i,j,k] <=1;
	
subject to arcos_saida_chegada {k in VEICULOS, j in NODOS}: 
	sum{(i,j) in ARCOS} x[i,j,k] = sum{(i,j) in ARCOS} x[j,i,k];

subject to cantidade_veiculos : 
    sum{k in VEICULOS, (1,j) in ARCOS}  x[1,j,k] <= card(VEICULOS);

subject to cantidade_veiculos_2 :  
    sum{k in VEICULOS, (i,1) in ARCOS}  x[i,1,k] <= card(VEICULOS);

subject to nao_subtours {(i,j) in ARCOS}: 
	sum{k in VEICULOS}x[i,j,k] + sum{k in VEICULOS}x[j,i,k] <= 1;
	
subject to topologias_radiais {k in VEICULOS}: 
	sum{(i,j) in ARCOS} x[i,j,k] <= card(NODOS);
	
#################################################################
# Restrições com o fluxo de mercadorias

subject to fluxo_mercadorias {j in CLIENTES}: 
    sum {k in VEICULOS, (i,j) in ARCOS}y[i,j,k] = sum {k in VEICULOS, (i,j) in ARCOS} y[j,i,k] + demanda[j] ;
    
subject to fluxo_maximo {k in VEICULOS, (i,j) in ARCOS}: 
    y[i,j,k] <= capacidade_vei[k]*x[i,j,k];

subject to deposito  {k in VEICULOS}: 
    sum{(1,j) in ARCOS} y[1,j,k] <= capacidade_dep;
    
subject to fluxo_mercadorias_est {j in ESTACOES}: 
    sum {k in VEICULOS, (i,j) in ARCOS}y[i,j,k] - sum {k in VEICULOS, (i,j) in ARCOS} y[j,i,k]= 0 ;

##################################################################
# Restricoes com o estado de carga da bateria (SOC)

subject to fluxo_SOC {j in CLIENTES}: 
   sum {k in VEICULOS, (i,j) in ARCOS}z[i,j,k] = sum {k in VEICULOS, (i,j) in ARCOS} z[j,i,k] + sum{k in VEICULOS, (i,j) in ARCOS} (consumo[k]*distancia[i,j])*x[i,j,k];

subject to fluxo_SOC_maximo {k in VEICULOS, (i,j) in ARCOS}: 
     z[i,j,k] <= SOC_max[k]*x[i,j,k];

subject to SOC_saida_minima{k in VEICULOS}: 
     sum{(1,j) in ARCOS} z[1,j,k] =  alpha* SOC_max[k]* sum{(1,j) in ARCOS}x[1,j,k];

subject to SOC_chegada{k in VEICULOS}: 
     sum{(i,1) in ARCOS} z[i,1,k] >= sum{(i,1) in ARCOS}(beta* SOC_max[k]+(consumo[k]*distancia[i,1]))*x[i,1,k];
     
##################################################################
# Restricoes das estacoes de carregamento

subject to SOC_chegada_EST  {k in VEICULOS, j in ESTACOES}: 
    sum {i in DUC} z[i,j,k] >= sum{i in DUC} (beta* SOC_max[k]+(consumo[k]*distancia[i,j]))*x[i,j,k]; 

subject to SOC_saida_maxima_est  {k in VEICULOS, i in ESTACOES}: 
    sum{j in DUC} z[i,j,k] <= alpha* SOC_max[k]* sum{j in DUC} x[i,j,k];
    
subject to SOC_saida_maxima_est_2  {k in VEICULOS, i in ESTACOES}: 
    sum{j in DUC} z[i,j,k] >= beta* SOC_max[k]* sum{j in DUC} x[i,j,k];

################################################################
# Restricoes do tempo

subject to fluxo_tiempo {j in CLIENTES}: 
    sum {k in VEICULOS,(i,j)in ARCOS}t[j,i,k] = sum {k in VEICULOS,(i,j)in ARCOS} t[i,j,k] + sum {k in VEICULOS,(i,j)in ARCOS} (tempo[i,j]+servico[j])*x[i,j,k] ;

subject to fluxo_tiempo_maximo{k in VEICULOS,(i,j) in ARCOS}: 
    t[j,i,k]<= (ultimo[j]+servico[j])*x[j,i,k];
 
subject to fluxo_tiempo_minimo {k in VEICULOS,(i,j)in ARCOS}: 
    t[j,i,k]>= (inicio[j])*x[j,i,k];

subject to fluxo_tiempo_est {j in ESTACOES}: 
    sum {k in VEICULOS,(i,j)in ARCOS}t[j,i,k] = sum {k in VEICULOS,(i,j)in ARCOS} t[i,j,k] + sum {k in VEICULOS,(i,j)in ARCOS} (tempo[i,j])*x[i,j,k]+sum {k in VEICULOS}w[j,k];
    
subject to fluxo_SOC_2 {j in ESTACOES,k in VEICULOS}: 
    sum {(i,j) in ARCOS}z[i,j,k] + velocidad_carga[k]*w[j,k] =  sum {(i,j) in ARCOS} z[j,i,k] +  sum {(i,j) in ARCOS}(consumo[k]*distancia[i,j])*x[i,j,k];

subject to fluxo_carga_est_2 {k in VEICULOS,j in ESTACOES}: 
     w[j,k] <= M*sum{i in DUC}x[i,j,k];