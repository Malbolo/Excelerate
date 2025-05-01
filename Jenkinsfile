pipeline {
  agent any

  environment {
    VITE_BASE_URL = ''
  }

  stages {
    stage('Detect changed services') {
      steps {
        script {
          def changedPaths = sh(
            script: '''git diff --name-only HEAD~1 HEAD''',
            returnStdout: true
          ).trim().split('\n')

          def targets = []

          for (path in changedPaths) {
            if (path.startsWith('frontend/')) {
              targets << 'frontend'
            } else if (path.startsWith('backend/')) {
              def subdir = path.split('/')[1]
              if (['agent-service', 'storage-service', 'notification-service'].contains(subdir)) {
                targets << "backend-${subdir}"
              }
            }
          }

          env.CHANGED_TARGETS = targets.unique().join(',')
          echo "Changed targets: ${env.CHANGED_TARGETS}"
        }
      }
    }

    stage('Build & Push Docker Images') {
      when {
        expression { return env.CHANGED_TARGETS }
      }
      steps {
        script {
          def targets = env.CHANGED_TARGETS.split(',')
          def BUILD_NUMBER = env.BUILD_NUMBER
          def GIT_COMMIT_SHORT = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()

          withCredentials([
            usernamePassword(credentialsId: 'dockerhub', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')
          ]) {
            for (target in targets) {
              def contextPath = ''
              def imageName = ''
              def imageTag = "${GIT_COMMIT_SHORT}-${BUILD_NUMBER}"

              if (target == 'frontend') {
                contextPath = 'frontend'
                imageName = "k12s101ss/react"

                withCredentials([string(credentialsId: 'VITE_BASE_URL', variable: 'VITE_BASE_URL')]) {
                  dir(contextPath) {
                    sh """
                      echo \$DOCKER_PASS | docker login -u \$DOCKER_USER --password-stdin
                      docker build \\
                        --build-arg VITE_BASE_URL=\$VITE_BASE_URL \\
                        -t ${imageName}:${imageTag} -t ${imageName}:latest .
                      docker push ${imageName}:${imageTag}
                      docker push ${imageName}:latest
                    """
                  }
                }
              } else if (target.startsWith('backend-')) {
                def serviceName = target.replace('backend-', '')
                contextPath = "backend/${serviceName}"
                imageName = "k12s101ss/backend-${serviceName}"

                dir(contextPath) {
                  sh """
                    echo \$DOCKER_PASS | docker login -u \$DOCKER_USER --password-stdin
                    docker build -t ${imageName}:${imageTag} -t ${imageName}:latest .
                    docker push ${imageName}:${imageTag}
                    docker push ${imageName}:latest
                  """
                }
              }
            }
          }
        }
      }
    }
  }
}
