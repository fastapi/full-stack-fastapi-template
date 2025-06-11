pipeline {
    agent any
    
    environment {
        DOCKER_REGISTRY = "${env.DOCKER_REGISTRY}"
        IMAGE_NAME = "${DOCKER_REGISTRY}/full-stack-fastapi-template"
        IMAGE_TAG = "${BUILD_NUMBER}-${GIT_COMMIT.take(7)}"
        GCP_VM_IP = "${env.GCP_VM_IP}"
        // NOTIFICATION_EMAIL = "${env.NOTIFICATION_EMAIL}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.GIT_COMMIT = sh(returnStdout: true, script: 'git rev-parse HEAD').trim()
                    env.BRANCH_NAME = env.BRANCH_NAME ?: sh(returnStdout: true, script: 'git rev-parse --abbrev-ref HEAD').trim()
                }
            }
        }
        
        // stage('Setup Environment') {
        //     steps {
        //         script {
        //             // Create .env file for testing
        //             sh '''
        //                 cp .env.example .env
        //                 echo "DATABASE_URL=postgresql://test:test@localhost:5432/test_db" >> .env
        //                 echo "SECRET_KEY=test-secret-key-for-ci" >> .env
        //             '''
        //         }
        //     }
        // }
        
        // stage('Backend Unit Tests') {
        //     when {
        //         anyOf {
        //             branch 'dev'
        //             changeRequest()
        //         }
        //     }
        //     steps {
        //         script {
        //             try {
        //                 sh '''
        //                     # Start test database
        //                     docker run -d --name test-postgres \
        //                         -e POSTGRES_USER=test \
        //                         -e POSTGRES_PASSWORD=test \
        //                         -e POSTGRES_DB=test_db \
        //                         -p 5432:5432 \
        //                         postgres:15-alpine
                            
        //                     # Wait for database to be ready
        //                     sleep 10
                            
        //                     # Install Python dependencies and run tests
        //                     python -m venv venv
        //                     source venv/bin/activate
        //                     pip install -r backend/requirements.txt
        //                     pip install pytest pytest-asyncio httpx
                            
        //                     # Run backend tests
        //                     cd backend
        //                     python -m pytest tests/ -v --tb=short
        //                 '''
        //             } catch (Exception e) {
        //                 currentBuild.result = 'FAILURE'
        //                 error("Backend tests failed: ${e.getMessage()}")
        //             } finally {
        //                 // Cleanup test database
        //                 sh 'docker rm -f test-postgres || true'
        //             }
        //         }
        //     }
        // }
        
        // stage('Frontend Unit Tests') {
        //     when {
        //         anyOf {
        //             branch 'dev'
        //             changeRequest()
        //         }
        //     }
        //     steps {
        //         script {
        //             try {
        //                 sh '''
        //                     cd frontend
        //                     npm ci
        //                     npm run test:unit
        //                     npm run build
        //                 '''
        //             } catch (Exception e) {
        //                 currentBuild.result = 'FAILURE'
        //                 error("Frontend tests failed: ${e.getMessage()}")
        //             }
        //         }
        //     }
        // }
        
        // stage('End-to-End Tests') {
        //     when {
        //         anyOf {
        //             branch 'dev'
        //             changeRequest()
        //         }
        //     }
        //     steps {
        //         script {
        //             try {
        //                 sh '''
        //                     # Start the full application stack for E2E tests
        //                     docker-compose -f docker-compose.test.yml up -d
                            
        //                     # Wait for services to be ready
        //                     sleep 30
                            
        //                     # Run Playwright E2E tests
        //                     cd frontend
        //                     npx playwright install
        //                     npx playwright test
        //                 '''
        //             } catch (Exception e) {
        //                 currentBuild.result = 'FAILURE'
        //                 error("E2E tests failed: ${e.getMessage()}")
        //             } finally {
        //                 // Cleanup test environment
        //                 sh 'docker-compose -f docker-compose.test.yml down -v || true'
        //             }
        //         }
        //     }
        // }
        
        stage('Wait for PR Approval') {
            when {
                changeRequest()
            }
            steps {
                script {
                    echo "Pull Request detected. Waiting for approval..."
                    // This stage will pause until PR is approved
                    input message: 'Approve this Pull Request?', ok: 'Approve',
                          submitterParameter: 'APPROVER'
                }
            }
        }
        
        stage('Build Docker Images') {
            when {
                branch 'main'
            }
            steps {
                script {
                    try {
                        // Build backend image
                        sh '''
                            docker build -t ${IMAGE_NAME}-backend:${IMAGE_TAG} \
                                -t ${IMAGE_NAME}-backend:latest \
                                -f backend/Dockerfile backend/
                        '''
                        
                        // Build frontend image
                        sh '''
                            docker build -t ${IMAGE_NAME}-frontend:${IMAGE_TAG} \
                                -t ${IMAGE_NAME}-frontend:latest \
                                -f frontend/Dockerfile frontend/
                        '''
                        
                        // Build reverse proxy image (if custom Traefik config)
                        // sh '''
                        //     docker build -t ${IMAGE_NAME}-proxy:${IMAGE_TAG} \
                        //         -t ${IMAGE_NAME}-proxy:latest \
                        //         -f proxy/Dockerfile proxy/
                        // '''
                    } catch (Exception e) {
                        currentBuild.result = 'FAILURE'
                        error("Docker build failed: ${e.getMessage()}")
                    }
                }
            }
        }
        
        stage('Push to Docker Registry') {
            when {
                branch 'main'
            }
            steps {
                script {
                    try {
                        withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', 
                                       usernameVariable: 'DOCKER_USER', 
                                       passwordVariable: 'DOCKER_PASS')]) {
                            sh '''
                                echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
                                
                                # Push backend images
                                docker push ${IMAGE_NAME}-backend:${IMAGE_TAG}
                                docker push ${IMAGE_NAME}-backend:latest
                                
                                # Push frontend images
                                docker push ${IMAGE_NAME}-frontend:${IMAGE_TAG}
                                docker push ${IMAGE_NAME}-frontend:latest
                                
                                # Push proxy images
                                # docker push ${IMAGE_NAME}-proxy:${IMAGE_TAG}
                                # docker push ${IMAGE_NAME}-proxy:latest
                            '''
                        }
                    } catch (Exception e) {
                        currentBuild.result = 'FAILURE'
                        error("Docker push failed: ${e.getMessage()}")
                    }
                }
            }
        }
        
        stage('Deploy to Development') {
            when {
                branch 'main'
            }
            steps {
                script {
                    try {
                        sshagent(['gcp-vm-credentials']) {
                            sh '''
                                # Deploy to development environment
                                ssh -o StrictHostKeyChecking=no user@${GCP_VM_IP} "
                                    # Pull latest images
                                    docker pull ${IMAGE_NAME}-backend:latest
                                    docker pull ${IMAGE_NAME}-frontend:latest
                                    # docker pull ${IMAGE_NAME}-proxy:latest
                                    
                                    # Navigate to deployment directory
                                    cd /opt/app-dev
                                    
                                    # Update docker-compose file with new image tags
                                    sed -i 's|image: .*-backend:.*|image: ${IMAGE_NAME}-backend:latest|' docker-compose.yml
                                    sed -i 's|image: .*-frontend:.*|image: ${IMAGE_NAME}-frontend:latest|' docker-compose.yml
                                    # sed -i 's|image: .*-proxy:.*|image: ${IMAGE_NAME}-proxy:latest|' docker-compose.yml
                                    
                                    # Deploy with zero-downtime
                                    docker-compose up -d --force-recreate --remove-orphans
                                    
                                    # Health check
                                    sleep 30
                                    curl -f http://localhost/api/health || exit 1
                                "
                            '''
                        }
                    } catch (Exception e) {
                        currentBuild.result = 'FAILURE'
                        error("Deployment to dev failed: ${e.getMessage()}")
                    }
                }
            }
        }
        
        stage('Deploy to Production') {
            when {
                allOf {
                    branch 'main'
                    not { changeRequest() }
                }
            }
            steps {
                script {
                    // Manual approval for production deployment
                    input message: 'Deploy to Production?', 
                          ok: 'Deploy',
                          submitterParameter: 'DEPLOYER'
                    
                    try {
                        sshagent(['gcp-vm-credentials']) {
                            sh '''
                                # Deploy to production environment
                                ssh -o StrictHostKeyChecking=no user@${GCP_VM_IP} "
                                    # Pull latest images
                                    docker pull ${IMAGE_NAME}-backend:${IMAGE_TAG}
                                    docker pull ${IMAGE_NAME}-frontend:${IMAGE_TAG}
                                    # docker pull ${IMAGE_NAME}-proxy:${IMAGE_TAG}
                                    
                                    # Navigate to production deployment directory
                                    cd /opt/app-prod
                                    
                                    # Update docker-compose file with specific image tags
                                    sed -i 's|image: .*-backend:.*|image: ${IMAGE_NAME}-backend:${IMAGE_TAG}|' docker-compose.yml
                                    sed -i 's|image: .*-frontend:.*|image: ${IMAGE_NAME}-frontend:${IMAGE_TAG}|' docker-compose.yml
                                    # sed -i 's|image: .*-proxy:.*|image: ${IMAGE_NAME}-proxy:${IMAGE_TAG}|' docker-compose.yml
                                    
                                    # Blue-green deployment strategy
                                    docker-compose up -d --scale backend=2 --scale frontend=2
                                    sleep 30
                                    
                                    # Health check
                                    curl -f https://your-domain.com/api/health || exit 1
                                    
                                    # Scale down old containers
                                    docker-compose up -d --scale backend=1 --scale frontend=1 --remove-orphans
                                "
                            '''
                        }
                    } catch (Exception e) {
                        currentBuild.result = 'FAILURE'
                        error("Production deployment failed: ${e.getMessage()}")
                    }
                }
            }
        }
        
        // stage('Post-Deployment Monitoring') {
        //     when {
        //         branch 'main'
        //     }
        //     steps {
        //         script {
        //             try {
        //                 // Run post-deployment health checks
        //                 sh '''
        //                     # Wait for services to stabilize
        //                     sleep 60
                            
        //                     # Run comprehensive health checks
        //                     curl -f http://${GCP_VM_IP}/api/health
        //                     curl -f http://${GCP_VM_IP}/
                            
        //                     # Check database connectivity
        //                     curl -f http://${GCP_VM_IP}/api/health/db
        //                 '''
                        
        //                 echo "Deployment successful! Monitoring alerts are active."
        //             } catch (Exception e) {
        //                 currentBuild.result = 'UNSTABLE'
        //                 echo "Deployment completed but health checks failed: ${e.getMessage()}"
        //             }
        //         }
        //     }
        // }
    }
    
    post {
        always {
            // Cleanup
            sh '''
                docker system prune -f
                rm -f .env
            '''
        }
        
        // success {
        //     emailext (
        //         subject: "✅ Pipeline Success: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
        //         body: """
        //             Pipeline executed successfully!
                    
        //             Job: ${env.JOB_NAME}
        //             Build: ${env.BUILD_NUMBER}
        //             Branch: ${env.BRANCH_NAME}
        //             Commit: ${env.GIT_COMMIT}
                    
        //             View build: ${env.BUILD_URL}
        //         """,
        //         to: "${NOTIFICATION_EMAIL}"
        //     )
        // }
        
        // failure {
        //     emailext (
        //         subject: "❌ Pipeline Failed: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
        //         body: """
        //             Pipeline execution failed!
                    
        //             Job: ${env.JOB_NAME}
        //             Build: ${env.BUILD_NUMBER}
        //             Branch: ${env.BRANCH_NAME}
        //             Commit: ${env.GIT_COMMIT}
                    
        //             Please check the logs: ${env.BUILD_URL}console
                    
        //             Error Details:
        //             ${env.BUILD_LOG}
        //         """,
        //         to: "${NOTIFICATION_EMAIL}"
        //     )
        // }
        
        // unstable {
        //     emailext (
        //         subject: "⚠️ Pipeline Unstable: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
        //         body: """
        //             Pipeline completed with warnings!
                    
        //             Job: ${env.JOB_NAME}
        //             Build: ${env.BUILD_NUMBER}
        //             Branch: ${env.BRANCH_NAME}
                    
        //             Please review: ${env.BUILD_URL}
        //         """,
        //         to: "${NOTIFICATION_EMAIL}"
        //     )
        // }
    }
}