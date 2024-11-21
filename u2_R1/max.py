from flask import Flask, request, jsonify
from http import HTTPStatus
from typing import Dict, Any

app = Flask(__name__)

class PetRegistry: # clase que atuara como un registro de mascotas en memoria , Permite realizar operaciones CRUD  acerca de las mascotas
    def __init__(self):
        self.pets: Dict[str, Dict[str, Any]] = {
            "M001": {
                "nombre_mascota": "Rocky",
                "edad_mascota": "2 años",
                "tipo_raza": "Bulldog",
                "alergias_conocidas": "Ninguna",
                "sexo_mascota": "Macho",
                "notas_adicionales": "Le gusta jugar con pelotas"
            },
            "M002": {
                "nombre_mascota": "Nina",
                "edad_mascota": "4 años",
                "tipo_raza": "Persa",
                "alergias_conocidas": "Pollo",
                "sexo_mascota": "Hembra",
                "notas_adicionales": "Muy tranquila"
            }
        }

    def obtener_mascotas(self) -> Dict:   #Obtiene todas las mascotas registradas
        return self.pets
    
    def buscar_mascotas(self, nombre: str = None, raza: str = None) -> Dict:  #Busca mascotas por nombre o raza, nombre de la mascota raza ,Raza de la mascota.
        return {
            id: datos for id, datos in self.pets.items()
            if (nombre and datos["nombre_mascota"].lower() == nombre.lower()) or 
               (raza and datos["tipo_raza"].lower() == raza.lower())
        }
    
    def registrar_mascota(self, id_mascota: str, datos: Dict) -> bool:    #Registra una nueva mascota si el ID y el nombre no están duplicados. Returns: True si el registro es exitoso, False en caso contrario.
        if id_mascota in self.pets:
            return False
        
        if any(m["nombre_mascota"].lower() == datos["nombre_mascota"].lower() 
               for m in self.pets.values()):
            return False
        
        self.pets[id_mascota] = datos
        return True
    
    def actualizar_mascota(self, id_mascota: str, datos: Dict) -> bool:    #Actualiza los datos de una mascota si existe y no hay duplicado de nombre.
        if id_mascota not in self.pets:
            return False
            
        if any(m["nombre_mascota"].lower() == datos["nombre_mascota"].lower() 
               and mid != id_mascota for mid, m in self.pets.items()):
            return False
            
        self.pets[id_mascota] = datos
        return True
    
    def eliminar_mascota(self, id_mascota: str) -> bool:   #Elimina una mascota por su ID si existe.
        if id_mascota not in self.pets:
            return False
        del self.pets[id_mascota]
        return True

registro = PetRegistry()

@app.route('/mascotas', methods=['GET'])    #    Endpoint para listar todas las mascotas registradas.
def listar_mascotas():
    return jsonify(registro.obtener_mascotas()), HTTPStatus.OK

@app.route('/mascotas/buscar', methods=['GET'])   #    Endpoint para buscar mascotas por nombre o raza.
def buscar_mascotas():
    nombre = request.args.get('nombre')
    raza = request.args.get('raza')
    resultados = registro.buscar_mascotas(nombre, raza)
    
    if not resultados:
        return jsonify({
            "estado": "error",
            "mensaje": "No se encontraron mascotas con esos criterios"
        }), HTTPStatus.NOT_FOUND
    
    return jsonify(resultados), HTTPStatus.OK

@app.route('/mascotas', methods=['POST'])      # Endpoint para registrar una nueva mascota.
def registrar_mascota():
    try:
        datos = request.get_json()
        campos_requeridos = [
            "id_mascota", "nombre_mascota", "edad_mascota", "tipo_raza",
            "alergias_conocidas", "sexo_mascota", "notas_adicionales"
        ]
        
        # Verificar que estén todos los campos necesarios
        if not all(campo in datos for campo in campos_requeridos):
            return jsonify({
                "estado": "error",
                "mensaje": "Faltan datos obligatorios de la mascota"
            }), HTTPStatus.BAD_REQUEST
        
        datos_mascota = {
            "nombre_mascota": datos["nombre_mascota"],
            "edad_mascota": datos["edad_mascota"],
            "tipo_raza": datos["tipo_raza"],
            "alergias_conocidas": datos["alergias_conocidas"],
            "sexo_mascota": datos["sexo_mascota"],
            "notas_adicionales": datos["notas_adicionales"]
        }
        
        if registro.registrar_mascota(datos["id_mascota"], datos_mascota):
            return jsonify({
                "estado": "exitoso",
                "mensaje": "Mascota registrada correctamente"
            }), HTTPStatus.CREATED
        else:
            return jsonify({
                "estado": "error",
                "mensaje": "Ya existe una mascota con ese ID o nombre"
            }), HTTPStatus.BAD_REQUEST
            
    except Exception as e:
        return jsonify({
            "estado": "error",
            "mensaje": f"Error en el servidor: {str(e)}"
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@app.route('/mascotas/<id_mascota>', methods=['PUT']) # Endpoint para actualizar una mascota existente
def actualizar_mascota(id_mascota):
    try:
        datos = request.get_json()
        campos_requeridos = [
            "nombre_mascota", "edad_mascota", "tipo_raza",
            "alergias_conocidas", "sexo_mascota", "notas_adicionales"
        ]
        
        if not all(campo in datos for campo in campos_requeridos):
            return jsonify({
                "estado": "error",
                "mensaje": "Faltan datos obligatorios de la mascota"
            }), HTTPStatus.BAD_REQUEST
        
        datos_mascota = {
            "nombre_mascota": datos["nombre_mascota"],
            "edad_mascota": datos["edad_mascota"],
            "tipo_raza": datos["tipo_raza"],
            "alergias_conocidas": datos["alergias_conocidas"],
            "sexo_mascota": datos["sexo_mascota"],
            "notas_adicionales": datos["notas_adicionales"]
        }
        
        if registro.actualizar_mascota(id_mascota, datos_mascota):
            return jsonify({
                "estado": "exitoso",
                "mensaje": "Datos de la mascota actualizados"
            }), HTTPStatus.OK
        else:
            return jsonify({
                "estado": "error",
                "mensaje": "Mascota no encontrada o nombre duplicado"
            }), HTTPStatus.NOT_FOUND
            
    except Exception as e:
        return jsonify({
            "estado": "error",
            "mensaje": f"Error en el servidor: {str(e)}"
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@app.route('/mascotas/<id_mascota>', methods=['DELETE']) # Endpoint para eliminar una mascota existente
def eliminar_mascota(id_mascota):
    if registro.eliminar_mascota(id_mascota):
        return jsonify({
            "estado": "exitoso",
            "mensaje": "Mascota eliminada correctamente"
        }), HTTPStatus.OK
    else:
        return jsonify({
            "estado": "error",
            "mensaje": "Mascota no encontrada"
        }), HTTPStatus.NOT_FOUND

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)