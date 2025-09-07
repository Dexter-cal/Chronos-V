# Chrono Hub Frontend

This directory contains the source code for the Chrono Hub, the main user-facing application for the Chrono Verse ecosystem.

## Purpose

The Chrono Hub is intended to be the central portal for players. It will feature:
- A library of all available and installed games built with the Chrono Verse engine.
- A marketplace for trading in-game assets, skins, and other user-generated content.
- Player profiles and social features.

This project was bootstrapped with [Vite](https://vitejs.dev/) and uses [React](https://reactjs.org/).

## Setup

To install the necessary dependencies, run the following command from the root of this `frontend` directory:
```bash
npm install
```

## ⚠️ Known Environment Issue

**Important:** The current execution environment has a critical issue with its `npm` installation. The `npm install` command completes but **fails to create the necessary binary links** in the `node_modules/.bin` directory.

This means that standard `npm` scripts like `npm run dev` or `npm run build` will fail with a `vite: not found` error.

Due to this issue, the application cannot currently be run or tested in this environment. The source code has been committed to save progress, but it is unverified.
