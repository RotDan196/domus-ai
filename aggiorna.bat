@echo off
title Domus AI - Auto Updater
color 0A
echo ---------------------------------------------------
echo 🚀 AVVIO AGGIORNAMENTO AUTOMATICO DOMUS AI
echo ---------------------------------------------------
echo.

:: 1. Aggiunge tutti i file modificati
echo [1/3] Aggiungo i nuovi file...
git add .

:: 2. Crea il salvataggio (Commit)
echo [2/3] Salvo le modifiche...
git commit -m "Aggiornamento automatico UI e Funzioni"

:: 3. Spedisce a GitHub (che avvisa Render)
echo [3/3] Spedisco al server online...
git push origin main

echo.
echo ---------------------------------------------------
echo ✅ FATTO! Render sta aggiornando il sito ora.
echo Attendi 2 minuti e controlla online.
echo ---------------------------------------------------
pause