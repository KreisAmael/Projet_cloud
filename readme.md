# Documentation Technique du Système RAG

## 1. Architecture du Système
Le système RAG (Retrieval-Augmented Generation) repose sur une architecture modulaire composée de quatre microservices principaux, développés avec FastAPI. Ces microservices communiquent entre eux pour fournir des réponses enrichies aux requêtes des utilisateurs. L'architecture repose sur les concepts suivants :

1. **Gestion des Documents** : Stockage et récupération des documents pertinents pour chaque requête.
2. **Récupération d'Informations** : Recherche des documents pertinents à l'aide de techniques d'embedding et de similarité cosinus.
3. **Génération de Réponse** : Utilisation d'un modèle de génération (T5-small dans ce cas) pour produire une réponse basée sur les documents récupérés.
4. **Gestion des Requêtes** : Orchestration des interactions entre les services pour traiter la requête utilisateur.

L'ensemble est conteneurisé avec Docker et orchestré via Kubernetes pour assurer scalabilité, portabilité et résilience.

---

## 2. Rôle de Chaque Microservice

### 2.1. Gestion des Documents (Document Management)
- **Rôle** : Ce service permet d'ajouter, de récupérer et de gérer les documents dans une base de données ou un stockage local.
- **Fonctionnalités** :
  - Ajout de documents avec génération automatique d'embeddings.
  - Récupération de documents par ID.
  - Liste des documents disponibles.
  - Suppression de documents.
- **Endpoints principaux** :
  - `POST /documents` : Ajouter un document.
  - `GET /documents/{doc_id}` : Récupérer un document par ID.
  - `GET /documents` : Lister tous les documents.

### 2.2. Récupération d'Informations (Information Retrieval)
- **Rôle** : Identifier les documents les plus pertinents pour une requête donnée.
- **Fonctionnalités** :
  - Génération d'un embedding pour une requête utilisateur.
  - Calcul de la similarité cosinus entre l'embedding de la requête et les embeddings des documents.
  - Renvoi des documents les plus pertinents.
- **Endpoints principaux** :
  - `POST /retrieve_documents` : Récupérer les documents pertinents à partir d'une requête utilisateur.

### 2.3. Génération de Réponse (Response Generation)
- **Rôle** : Produire une réponse enrichie en utilisant un modèle de génération (T5-small).
- **Fonctionnalités** :
  - Prendre une requête et une liste de documents.
  - Générer une réponse textuelle en se basant sur le contexte fourni par les documents.
- **Endpoints principaux** :
  - `POST /rag` : Générer une réponse à partir d'une requête et de documents associés.

### 2.4. Gestion des Requêtes (Query Manager)
- **Rôle** : Orchestrer le flux de traitement des requêtes utilisateurs.
- **Fonctionnalités** :
  - Recevoir une requête utilisateur.
  - Appeler le service de récupération pour obtenir les documents pertinents.
  - Passer les résultats au service de génération pour produire une réponse.
- **Endpoints principaux** :
  - `POST /retrieve` : Appeler le service de récupération pour trouver les documents pertinents.
  - `POST /generate` : Générer une réponse enrichie.

---

## 3. Déploiement et Tests des Services

### 3.1. Conteneurisation avec Docker
Pour préparer les images Docker en local :

1. Construire les images Docker pour chaque microservice. Voici les commandes :
   ```bash
   docker build -t documents_service:latest -f Dockerfile.documents_service .
   docker build -t retrieval_service:latest -f Dockerfile.retrieval_service .
   docker build -t generation_service:latest -f Dockerfile.generation_service .
   docker build -t user_request_service:latest -f Dockerfile.user_request_service .
   ```

2. Vérifier que les images sont bien créées :
   ```bash
   docker images
   ```

3. Pousser les images Docker dans le registre local pour qu'elles soient accessibles par Kubernetes :
   ```bash
   kind load docker-image documents_service:latest
   kind load docker-image retrieval_service:latest
   kind load docker-image generation_service:latest
   kind load docker-image user_request_service:latest
   ```

### 3.2. Orchestration avec Kubernetes
Les fichiers YAML suivants sont utilisés pour déployer les services dans Kubernetes :

1. **Déployer les fichiers YAML** :
   ```bash
   kubectl apply -f ./k8s/documents_service/deployment.yaml
   kubectl apply -f ./k8s/documents_service/service.yaml
   kubectl apply -f ./k8s/retrieval_service/deployment.yaml
   kubectl apply -f ./k8s/retrieval_service/service.yaml
   kubectl apply -f ./k8s/generation_service/deployment.yaml
   kubectl apply -f ./k8s/generation_service/service.yaml
   kubectl apply -f ./k8s/user_request_service/deployment.yaml
   kubectl apply -f ./k8s/user_request_service/service.yaml
   ```

2. **Vérifier les Pods et Services déployés** :
   ```bash
   kubectl get pods
   kubectl get services
   ```

3. **Tester dans Kubernetes** :
   - Accéder à Swagger UI pour chaque service :
     ```
     http://<IP-du-service>:800X/docs
     ```

---

## 4. Interaction entre les Services (Système RAG Complet)

Le système RAG fonctionne comme suit :

1. **Entrée utilisateur** :
   - L'utilisateur envoie une requête via le service de gestion des requêtes.
2. **Récupération des documents** :
   - Le service de gestion des requêtes appelle le service de récupération pour identifier les documents les plus pertinents en calculant la similarité entre l'embedding de la requête et ceux des documents.
3. **Génération de la réponse** :
   - Les documents pertinents sont envoyés au service de génération, qui utilise le modèle T5-small pour produire une réponse enrichie.
4. **Retour de la réponse** :
   - La réponse est renvoyée à l'utilisateur via le service de gestion des requêtes.

Cette interaction permet d'intégrer efficacement les étapes de récupération d'informations et de génération de texte pour fournir des réponses contextuelles et pertinentes.

