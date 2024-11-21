#R1 U2 APIS  Jared Maximiliano Balderas Domínguez.

from flask import Flask, request, jsonify
from http import HTTPStatus
from typing import Dict, Any

app = Flask(__name__)

class AsignaturaRegistry:
    def __init__(self):
        self.asignaturas: Dict[str, Dict[str, Any]] = {}

    def obtener_asignaturas(self) -> Dict:
        return self.asignaturas
    
    def buscar_asignaturas(self, clave: str = None, nombre: str = None) -> Dict:
        return {
            clave: datos for clave, datos in self.asignaturas.items()
            if (clave and clave.lower() == clave.lower()) or 
               (nombre and datos["nombre"].lower() == nombre.lower())
        }
    
    def registrar_asignatura(self, clave_asignatura: str, datos: Dict) -> bool:
        if clave_asignatura in self.asignaturas:
            return False
        
        self.asignaturas[clave_asignatura] = datos
        return True
    
    def eliminar_asignatura(self, clave_asignatura: str) -> bool:
        if clave_asignatura not in self.asignaturas:
            return False
        del self.asignaturas[clave_asignatura]
        return True

registro = AsignaturaRegistry()

@app.route('/asignaturas', methods=['GET'])
def listar_asignaturas():
    return jsonify(registro.obtener_asignaturas()), HTTPStatus.OK

@app.route('/asignaturas/buscar', methods=['GET'])
def buscar_asignaturas():
    clave = request.args.get('clave')
    nombre = request.args.get('nombre')
    
    if not clave and not nombre:
        return jsonify({
            "estado": "error",
            "mensaje": "Los parámetros clave y nombre no pueden estar vacíos, todo de eso"
        }), HTTPStatus.BAD_REQUEST
    
    resultados = registro.buscar_asignaturas(clave, nombre)
    
    if not resultados:
        return jsonify({
            "estado": "error",
            "mensaje": "No se encontraron asignaturas con esos criterios"
        }), HTTPStatus.NOT_FOUND
    
    return jsonify(resultados), HTTPStatus.OK

@app.route('/asignaturas', methods=['POST'])
def registrar_asignatura():
    try:
        datos = request.get_json()
        campos_requeridos = [
            "clave", "nombre", "horas_semana", "horas_cuatrimestre",
            "cuatrimestre", "carrera"
        ]
        
        # Verificar si si andan ahí los campos necesarios todo de eso
        if not all(campo in datos for campo in campos_requeridos):
            return jsonify({
                "estado": "error",
                "mensaje": "Faltan datos obligatorios de la asignatura"
            }), HTTPStatus.BAD_REQUEST
        
        # Validaciones adicionales OJOO
        if not (0 <= datos["horas_semana"] <= 15):
            return jsonify({
                "estado": "error",
                "mensaje": "Horas por semana deben estar entre 0 y 15, asi es"
            }), HTTPStatus.BAD_REQUEST
        
        if not (1 <= datos["horas_cuatrimestre"] <= 5):
            return jsonify({
                "estado": "error",
                "mensaje": "Horas por cuatrimestre deben estar entre 1 y 5"
            }), HTTPStatus.BAD_REQUEST
        
        carreras_validas = ["Redes digitales", "Desarrollo de software", "Entornos virtuales"]
        if datos["carrera"] not in carreras_validas:
            return jsonify({
                "estado": "error",
                "mensaje": f"La carrera debe ser una de las siguientes: {', '.join(carreras_validas)}"
            }), HTTPStatus.BAD_REQUEST
        
        if registro.registrar_asignatura(datos["clave"], datos):
            return jsonify({
                "estado": "exitoso",
                "mensaje": "Asignatura registrada correctamente"
            }), HTTPStatus.CREATED
        else:
            return jsonify({
                "estado": "error",
                "mensaje": "Ya existe una asignatura con esa clave"
            }), HTTPStatus.BAD_REQUEST
            
    except Exception as e:
        return jsonify({
            "estado": "error",
            "mensaje": f"Error en el servidor: {str(e)}"
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@app.route('/asignaturas/<clave_asignatura>', methods=['DELETE'])
def eliminar_asignatura(clave_asignatura):
    if registro.eliminar_asignatura(clave_asignatura):
        return jsonify({
            "estado": "exitoso",
            "mensaje": "Asignatura eliminada correctamente"
        }), HTTPStatus.OK
    else:
        return jsonify({
            "estado": "error",
            "mensaje": "No se encontró una asignatura con esa clave"
        }), HTTPStatus.NOT_FOUND

if __name__ == '__main__':
    app.run(debug=True)

