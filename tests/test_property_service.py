import unittest
from unittest.mock import MagicMock
from app.property_service import PropertyService
from app.models import PropertyAPIResponseDTO
from app.database_manager import DatabaseManager


class TestPropertyService(unittest.TestCase):

    def setUp(self):
        self.mock_db_manager = MagicMock(spec=DatabaseManager)
        self.propertyService = PropertyService(db_manager=self.mock_db_manager)

    def test_get_properties_no_filters_success(self):
        """
        Prueba get_properties sin filtros y con resultados exitosos de la BD.
        """
        # Arrange
        sample_db_return = [
            {"address": "Calle 1", "city": "Bogota", "current_status": "en_venta",
                "price": 100, "description": "Desc 1"},
            {"address": "Calle 2", "city": "Medellin",
                "current_status": "pre_venta", "price": 200, "description": "Desc 2"},
        ]
        self.mock_db_manager.fetch_all.return_value = sample_db_return

        # Act
        result = self.propertyService.get_properties(filters={})

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], PropertyAPIResponseDTO)
        self.assertEqual(result[0].direccion, "Calle 1")
        self.assertEqual(result[0].ciudad, "Bogota")
        self.assertEqual(result[0].estado, "en_venta")
        self.assertEqual(result[1].precio_venta, 200)

        self.mock_db_manager.fetch_all.assert_called_once()
        args, kwargs = self.mock_db_manager.fetch_all.call_args
        called_sql_query = args[0]
        self.assertIn("s.name IN (%s, %s, %s)", called_sql_query)
        self.assertIn("pre_venta", args[1])
        self.assertIn("en_venta", args[1])
        self.assertIn("vendido", args[1])

    def test_get_properties_with_city_filter(self):
        """
        Prueba get_properties con un filtro de ciudad.
        """
        sample_db_return = [
            {"address": "Calle Sol", "city": "Cartagena", "current_status": "vendido",
                "price": 300, "description": "Frente al mar"}
        ]
        self.mock_db_manager.fetch_all.return_value = sample_db_return

        filters = {"city": "Cartagena"}
        result = self.propertyService.get_properties(filters)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].ciudad, "Cartagena")

        self.mock_db_manager.fetch_all.assert_called_once()
        args, kwargs = self.mock_db_manager.fetch_all.call_args
        called_sql_query = args[0]
        called_params = args[1]

        self.assertIn("LOWER(p.city) LIKE LOWER(%s)", called_sql_query)
        self.assertIn("%Cartagena%", called_params)

    def test_get_properties_with_year_filter(self):
        """
        Prueba get_properties con un filtro de año.
        """
        self.mock_db_manager.fetch_all.return_value = [
            {"address": "Calle Luna", "city": "Bogota",
                "current_status": "en_venta", "price": 150, "description": "Nuevo"}
        ]
        filters = {"year": 2022}
        self.propertyService.get_properties(filters)

        self.mock_db_manager.fetch_all.assert_called_once()
        args, kwargs = self.mock_db_manager.fetch_all.call_args
        called_sql_query = args[0]
        called_params = args[1]

        self.assertIn("p.year = %s", called_sql_query)
        self.assertIn(2022, called_params)

    def test_get_properties_with_status_filter(self):
        """
        Prueba get_properties con un filtro de estado.
        """
        self.mock_db_manager.fetch_all.return_value = []
        filters = {"status": "pre_venta"}
        self.propertyService.get_properties(filters)

        self.mock_db_manager.fetch_all.assert_called_once()
        args, kwargs = self.mock_db_manager.fetch_all.call_args
        called_sql_query = args[0]
        called_params = args[1]

        self.assertIn("s.name = %s", called_sql_query)
        self.assertIn("pre_venta", called_params)
        self.assertTrue(called_sql_query.count("%s") >= 4)

    def test_get_properties_db_error(self):
        """
        Prueba get_properties cuando DatabaseManager.fetch_all devuelve None (simulando un error de BD).
        """
        self.mock_db_manager.fetch_all.return_value = None
        result = self.propertyService.get_properties(filters={})

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 0)
        self.mock_db_manager.fetch_all.assert_called_once()

    def test_get_properties_empty_db_result(self):
        """
        Prueba get_properties cuando la BD devuelve una lista vacía (sin resultados).
        """
        self.mock_db_manager.fetch_all.return_value = []

        result = self.propertyService.get_properties(
            filters={"city": "CiudadInexistente"})

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 0)
        self.mock_db_manager.fetch_all.assert_called_once()

    def test_get_properties_transformation_to_dto(self):
        """
        Prueba la transformación de los datos de la BD a PropertyAPIResponseDTO.
        """
        sample_db_return = [
            {"address": "Av Principal", "city": "Cali", "current_status": "vendido",
                "price": 250, "description": "Bien ubicado"},
        ]
        self.mock_db_manager.fetch_all.return_value = sample_db_return
        result = self.propertyService.get_properties(filters={})

        self.assertEqual(len(result), 1)
        prop_dto = result[0]
        self.assertIsInstance(prop_dto, PropertyAPIResponseDTO)
        self.assertEqual(prop_dto.direccion, "Av Principal")
        self.assertEqual(prop_dto.ciudad, "Cali")
        self.assertEqual(prop_dto.estado, "vendido")
        self.assertEqual(prop_dto.precio_venta, 250)
        self.assertEqual(prop_dto.descripcion, "Bien ubicado")

    def test_get_properties_key_error_in_transformation(self):
        """
        Prueba el manejo de KeyError si un campo esperado falta en los datos de la BD.
        """
        faulty_db_return = [
            {"address": "Calle Rota", "city": "ErrorCity",
                "price": 50, "description": "Dato incompleto"}
        ]
        self.mock_db_manager.fetch_all.return_value = faulty_db_return

        result = self.propertyService.get_properties(filters={})

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 0)


if __name__ == '__main__':
    unittest.main()
