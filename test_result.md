#====================================================================================================
# START - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================

# THIS SECTION CONTAINS CRITICAL TESTING INSTRUCTIONS FOR BOTH AGENTS
# BOTH MAIN_AGENT AND TESTING_AGENT MUST PRESERVE THIS ENTIRE BLOCK

# Communication Protocol:
# If the `testing_agent` is available, main agent should delegate all testing tasks to it.
#
# You have access to a file called `test_result.md`. This file contains the complete testing state
# and history, and is the primary means of communication between main and the testing agent.
#
# Main and testing agents must follow this exact format to maintain testing data. 
# The testing data must be entered in yaml format Below is the data structure:
# 
## user_problem_statement: {problem_statement}
## backend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.py"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## frontend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.js"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## metadata:
##   created_by: "main_agent"
##   version: "1.0"
##   test_sequence: 0
##   run_ui: false
##
## test_plan:
##   current_focus:
##     - "Task name 1"
##     - "Task name 2"
##   stuck_tasks:
##     - "Task name with persistent issues"
##   test_all: false
##   test_priority: "high_first"  # or "sequential" or "stuck_first"
##
## agent_communication:
##     -agent: "main"  # or "testing" or "user"
##     -message: "Communication message between agents"

# Protocol Guidelines for Main agent
#
# 1. Update Test Result File Before Testing:
#    - Main agent must always update the `test_result.md` file before calling the testing agent
#    - Add implementation details to the status_history
#    - Set `needs_retesting` to true for tasks that need testing
#    - Update the `test_plan` section to guide testing priorities
#    - Add a message to `agent_communication` explaining what you've done
#
# 2. Incorporate User Feedback:
#    - When a user provides feedback that something is or isn't working, add this information to the relevant task's status_history
#    - Update the working status based on user feedback
#    - If a user reports an issue with a task that was marked as working, increment the stuck_count
#    - Whenever user reports issue in the app, if we have testing agent and task_result.md file so find the appropriate task for that and append in status_history of that task to contain the user concern and problem as well 
#
# 3. Track Stuck Tasks:
#    - Monitor which tasks have high stuck_count values or where you are fixing same issue again and again, analyze that when you read task_result.md
#    - For persistent issues, use websearch tool to find solutions
#    - Pay special attention to tasks in the stuck_tasks list
#    - When you fix an issue with a stuck task, don't reset the stuck_count until the testing agent confirms it's working
#
# 4. Provide Context to Testing Agent:
#    - When calling the testing agent, provide clear instructions about:
#      - Which tasks need testing (reference the test_plan)
#      - Any authentication details or configuration needed
#      - Specific test scenarios to focus on
#      - Any known issues or edge cases to verify
#
# 5. Call the testing agent with specific instructions referring to test_result.md
#
# IMPORTANT: Main agent must ALWAYS update test_result.md BEFORE calling the testing agent, as it relies on this file to understand what to test next.

#====================================================================================================
# END - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================



#====================================================================================================
# Testing Data - Main Agent and testing sub agent both should log testing data below this section
#====================================================================================================

user_problem_statement: "Aplicación para analizar textos administrativos conforme a la Guía panhispánica de lenguaje claro (RAE). Detecta expresiones confusas y sugiere versiones más comprensibles. Usa OpenAI GPT-5.1 con Emergent LLM key. Incluye botones para aceptar/rechazar sugerencias y límite de 4000 caracteres."

backend:
  - task: "Endpoint POST /api/analyze para análisis de texto con OpenAI GPT-5.1"
    implemented: true
    working: "NA"
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Implementado endpoint /api/analyze con integración de OpenAI GPT-5.1 mediante emergentintegrations. Usa prompt especializado para análisis de lenguaje claro según RAE. Valida longitud máxima de 4000 caracteres. Devuelve JSON con sugerencias que incluyen: original, problema, sugerencia. Backend reiniciado correctamente."

frontend:
  - task: "Interfaz de usuario con textarea, botones aceptar/rechazar y vista previa de texto mejorado"
    implemented: true
    working: "NA"
    file: "/app/frontend/src/pages/HomePage.jsx"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Implementado UI completo con diseño en colores claros y azul agua (cyan/sky). Incluye: textarea con límite de 4000 caracteres y contador, botón de análisis, lista de sugerencias con badges de colores, botones Aceptar/Rechazar para cada sugerencia, vista previa del texto mejorado cuando se aceptan sugerencias, notificaciones toast. Integrado con backend real mediante axios llamando a POST /api/analyze."

metadata:
  created_by: "main_agent"
  version: "1.0"
  test_sequence: 0
  run_ui: false

test_plan:
  current_focus:
    - "Endpoint POST /api/analyze para análisis de texto con OpenAI GPT-5.1"
    - "Interfaz de usuario con textarea, botones aceptar/rechazar y vista previa de texto mejorado"
  stuck_tasks: []
  test_all: false
  test_priority: "high_first"

agent_communication:
  - agent: "main"
    message: "He implementado la aplicación completa de análisis de lenguaje claro. Backend con OpenAI GPT-5.1 usando EMERGENT_LLM_KEY y frontend con diseño en colores claros y azul agua. Necesito que pruebes: 1) POST /api/analyze con texto de prueba administrativo, 2) Verificar que el límite de 4000 caracteres funciona, 3) Probar que las sugerencias se generan correctamente, 4) Verificar que los botones Aceptar/Rechazar funcionan y actualizan la vista previa del texto mejorado. El prompt del sistema está optimizado según las especificaciones del usuario para análisis de textos administrativos según la Guía panhispánica de lenguaje claro."