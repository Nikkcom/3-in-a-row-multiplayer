import {createPlayingBoard, playMove, updateBoardOnWin} from "./threeinarow.js";

window.addEventListener("DOMContentLoaded", () => {

    // Initialize the playing board.
    const playingBoard = document.querySelector(".board");
    createPlayingBoard(playingBoard);

    // Opens a websocket connection
    const websocket = new WebSocket("ws://localhost:8001");

    // Register event handlers.
    receiveMoves(playingBoard, websocket);
    sendMoves(playingBoard, websocket);
})

// Displays an alert to the user.
function showMessage(message) {
    window.setTimeout(() => window.alert(message), 50);
}

function receiveMoves(playingBoard, websocket) {
    websocket.addEventListener("message", ({ data }) => {
        console.log("From Server: ", JSON.stringify(data, null, 2));
        const event = JSON.parse(data);
        switch (event.type) {
            case "PLAY":
                // In case of PLAY event. Update the UI with the opponents move.
                playMove(playingBoard, event.player, event.column, event.row);
                break;
            case "WIN":
                const winningPosition = event.winning_pos
                updateBoardOnWin(playingBoard, winningPosition);
                console.log("Called updateboard with" + winningPosition);
                showMessage(`Player ${event.player} wins!`)
                // This is the last expected message. So the websocket connection is closed.
                websocket.close(1000);
                break;
            case "ERROR":
                showMessage(event.message);
                break;
            default:
                throw new Error("Unknown event type " + event.type);
        }
    })
}
function sendMoves(playingBoard, websocket) {
    // Sends PLAY events to the server

    playingBoard.addEventListener("click", ({ target }) => {

        const column = target.dataset.column;
        if (column === undefined || column === null) {
            return;
        }
        const row = target.dataset.row;

        const event = {
            type: "PLAY",
            column: parseInt(column),
            row: parseInt(row),
        };
        websocket.send(JSON.stringify(event));
    })
}









