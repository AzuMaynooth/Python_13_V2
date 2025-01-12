document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector("form");

    form.addEventListener("submit", (event) => {
        const productName = document.getElementById("product-name").value.trim();
        const unitPrice = parseFloat(document.getElementById("unit-price").value);
        const numberOfPieces = parseInt(document.getElementById("number-of-pieces").value);

        let errorMessage = "";

        // Validar el nombre del producto
        if (!productName) {
            errorMessage += "Product name is required.\n";
        }

        // Validar el precio (debe ser un número positivo)
        if (isNaN(unitPrice) || unitPrice <= 0) {
            errorMessage += "Unit price must be a positive number.\n";
        }

        // Validar la cantidad (debe ser un número entero positivo)
        if (isNaN(numberOfPieces) || numberOfPieces <= 0) {
            errorMessage += "Number of pieces must be a positive integer.\n";
        }

        // Si hay errores, evitar el envío del formulario y mostrar los mensajes de error
        if (errorMessage) {
            event.preventDefault(); // Evita que el formulario se envíe
            alert(errorMessage); // Muestra los errores
        } else {
            // Si el formulario es válido, puedes proceder a enviarlo o mostrar un mensaje de éxito
            // Ya que el formulario se enviará al servidor automáticamente después de la validación
            alert("Purchase submitted successfully!");
        }
    });
});
