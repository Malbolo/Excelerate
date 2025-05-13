pipeline {
  agent any

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
              if (['agent-service', 'storage-service', 'notification-service', 'user-service', 'auth-service', 'job-service', 'schedule-service'].contains(subdir)) {
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

          withCredentials([usernamePassword(credentialsId: 'dockerhub', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
            for (target in targets) {
              def contextPath = ''
              def imageName = ''
              def imageTag = "${GIT_COMMIT_SHORT}-${BUILD_NUMBER}"

              if (target == 'frontend') {
                contextPath = 'frontend'
                imageName = "k12s101ss/react"
              } else if (target.startsWith('backend-')) {
                def serviceName = target.replace('backend-', '')
                contextPath = "backend/${serviceName}"
                imageName = "k12s101ss/${serviceName}"
              }

              echo "Building and pushing ${imageName}"

              dir(contextPath) {
                if (target == 'backend-user-service') {
                  sh './gradlew clean build -x test'
                }

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
