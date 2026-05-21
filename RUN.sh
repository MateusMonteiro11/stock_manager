#!/bin/bash
echo "Instalando dependencias..."
pip install -r requirements.txt
echo ""
echo "Iniciando Sistema de Estoque..."
python main.py
