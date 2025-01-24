const PLAYER_ONE = "cross";
const PLAYER_TWO = "circle";

function createPlayingBoard(board) {

    for (let column = 0; column < 3; column++) {
        const columnElement = document.createElement("div");
        columnElement.className = "column";
        for (let row = 0; row < 3; row++) {
            const cellElement = document.createElement("div");
            cellElement.classList.add("cell", "empty");
            cellElement.dataset.column = column;
            cellElement.dataset.row = row;
            columnElement.appendChild(cellElement);
        }
    board.append(columnElement);
    }
}

function playMove(board, player, column, row) {

    // Checks that the player value is valid.
    if (player !== PLAYER_ONE && player !== PLAYER_TWO) {
        throw new Error(`Player must be ${PLAYER_ONE} or ${ PLAYER_TWO}.`);
    }

    // Checks that the column value is valid.
    const columnElements = board.querySelectorAll(".column");
    if (column < 0 || column > 3) {
        throw new RangeError("Column must be between 0 and 2.");
    }

    const columnElement = columnElements[column];

    // Checks that the row value is valid.
    const cellElements = columnElement.querySelectorAll(".cell");
    if (row < 0 || row > 3) {
        throw new RangeError("Row must be between 0 and 2.");
    }
    const cellElement = cellElements[row];

    // Checks if cell is occupied.
    if (!cellElement.classList.contains("empty")) {
        throw new Error("Cell must be empty");
    }

    // Places the player symbol in the cell.
    cellElement.classList.replace("empty", player);
}

export {createPlayingBoard, playMove, PLAYER_ONE, PLAYER_TWO};
