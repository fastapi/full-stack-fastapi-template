pipeline {
  agent any

  environment {
    BRANCH = "${env.BRANCH_NAME}"
    SSH_USER = 'TaiKhau'
    GCP_VM_DEV = '34.87.10.98'
    GCP_VM_PROD = '34.87.10.98'
    DEPLOY_DIR = "/home/TaiKhau/app"
    // Adding Docker Hub variables
    DOCKER_HUB_CREDS = credentials('dockerhub-credentials')
    DOCKER_HUB_USERNAME = "${DOCKER_HUB_CREDS_USR}"
    DOCKER_IMAGE_PREFIX = "${DOCKER_HUB_USERNAME}"
    // Adding GitHub credentials
    GITHUB_TOKEN = credentials('github-token')
  }

  stages {
    stage('Checkout') {
      steps {
        git branch: "${BRANCH}", url: 'https://Qu11et:${GITHUB_TOKEN}@github.com/Qu11et/full-stack-fastapi-template.git'
      }
    }

    stage('Build and Test') {
      steps {
        echo "Running on branch: ${BRANCH}"

        script {
          if (BRANCH == 'Dev') {
            sh 'cp backend/.env.dev backend/.env'
          } else if (BRANCH == 'Main') {
            sh 'cp backend/.env.prod backend/.env'
          }
        }

        // Run unit tests, lint, etc.
      }
    }

    stage('Build Docker Images') {
      steps {
        script {
          docker.build("${DOCKER_IMAGE_PREFIX}/my-frontend:${BRANCH}", 'frontend')
          docker.build("${DOCKER_IMAGE_PREFIX}/my-backend:${BRANCH}", 'backend')
        }
      }
    }

    stage('Push Images to Docker Hub') {
      steps {
        // Login to Docker Hub
        sh "echo ${DOCKER_HUB_CREDS_PSW} | docker login -u ${DOCKER_HUB_CREDS_USR} --password-stdin"
        
        // Tag images with latest tag in addition to branch tag
        sh """
          docker tag ${DOCKER_IMAGE_PREFIX}/my-backend:${BRANCH} ${DOCKER_IMAGE_PREFIX}/my-backend:latest
          docker tag ${DOCKER_IMAGE_PREFIX}/my-frontend:${BRANCH} ${DOCKER_IMAGE_PREFIX}/my-frontend:latest
          
          # Push images with branch tag
          docker push ${DOCKER_IMAGE_PREFIX}/my-backend:${BRANCH}
          docker push ${DOCKER_IMAGE_PREFIX}/my-frontend:${BRANCH}
          
          # Push images with latest tag
          docker push ${DOCKER_IMAGE_PREFIX}/my-backend:latest
          docker push ${DOCKER_IMAGE_PREFIX}/my-frontend:latest
        """
        
        // Logout from Docker Hub
        sh "docker logout"
      }
    }

    stage('Deploy') {
      steps {
        sshagent(['gcp-vm-ssh-key']) {
          script {
            def target_ip = (BRANCH == 'Dev') ? GCP_VM_DEV : GCP_VM_PROD

            sh """
              ssh -o StrictHostKeyChecking=no $SSH_USER@$target_ip << EOF
                cd $DEPLOY_DIR
                docker pull ${DOCKER_IMAGE_PREFIX}/my-backend:${BRANCH}
                docker pull ${DOCKER_IMAGE_PREFIX}/my-frontend:${BRANCH}
                docker compose down
                docker compose up -d
              EOF
            """
          }
        }
      }
    }
  }

  post {
    success {
      echo "Deployment succeeded on branch ${BRANCH}"
    }
    failure {
      echo "Deployment failed on branch ${BRANCH}"
    }
  }
}
