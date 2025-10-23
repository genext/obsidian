---
title: "Enum"
created: 2024-11-13 14:47:32
updated: 2025-09-16 08:43:24
---
  * java
    * **Each constant** in an enum class is actually **an instance of the class**
      * When you define constants in an enum with **additional values**, each constant needs its **own unique values initialized** when it's created.
      * The enum **constructor** allows us to **set** those unique **values for each constant**.
    * example1 ^lyaa7Fg1l
      * ```java
// Example 1: Simple enum without constructor (default behavior)
enum SimpleDay {
    MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY
    // Each constant is an instance of SimpleDay class with no additional data
}

// Example 2: Enum with constructor and additional values
enum Planet {
    // Each constant is created by calling the constructor with specific values
    MERCURY(3.303e+23, 2.4397e6),
    VENUS(4.869e+24, 6.0518e6),
    EARTH(5.976e+24, 6.37814e6),
    MARS(6.421e+23, 3.3972e6),
    JUPITER(1.9e+27, 7.1492e7),
    SATURN(5.688e+26, 6.0268e7),
    URANUS(8.686e+25, 2.5559e7),
    NEPTUNE(1.024e+26, 2.4746e7);

    // Instance variables - each enum constant will have these
    private final double mass;   // in kilograms
    private final double radius; // in meters

    // Constructor - called when each constant is created
    Planet(double mass, double radius) {
        this.mass = mass;
        this.radius = radius;
    }

    // Instance methods - each enum constant can use these
    public double getMass() { 
        return mass; 
    }
    
    public double getRadius() { 
        return radius; 
    }

    // Calculate surface gravity
    public double surfaceGravity() {
        return 6.67300E-11 * mass / (radius * radius);
    }
}

// Example 3: Enum representing HTTP status codes
enum HttpStatus {
    OK(200, "OK"),
    NOT_FOUND(404, "Not Found"),
    INTERNAL_SERVER_ERROR(500, "Internal Server Error"),
    BAD_REQUEST(400, "Bad Request");

    private final int code;
    private final String message;

    // Constructor
    HttpStatus(int code, String message) {
        this.code = code;
        this.message = message;
    }

    public int getCode() {
        return code;
    }

    public String getMessage() {
        return message;
    }

    @Override
    public String toString() {
        return code + " " + message;
    }
}

// Example 4: More complex enum with methods
enum Operation {
    PLUS("+") {
        @Override
        public double apply(double x, double y) {
            return x + y;
        }
    },
    MINUS("-") {
        @Override
        public double apply(double x, double y) {
            return x - y;
        }
    },
    MULTIPLY("*") {
        @Override
        public double apply(double x, double y) {
            return x * y;
        }
    },
    DIVIDE("/") {
        @Override
        public double apply(double x, double y) {
            return x / y;
        }
    };

    private final String symbol;

    Operation(String symbol) {
        this.symbol = symbol;
    }

    public String getSymbol() {
        return symbol;
    }

    // Abstract method that each constant must implement
    public abstract double apply(double x, double y);

    @Override
    public String toString() {
        return symbol;
    }
}

// Demo class to show how enums work
public class EnumDemo {
    public static void main(String[] args) {
        System.out.println("=== Planet Example ===");
        // Each constant is an instance with its own values
        Planet earth = Planet.EARTH;
        System.out.println("Earth mass: " + earth.getMass());
        System.out.println("Earth radius: " + earth.getRadius());
        System.out.println("Earth surface gravity: " + earth.surfaceGravity());

        System.out.println("\n=== HTTP Status Example ===");
        HttpStatus status = HttpStatus.NOT_FOUND;
        System.out.println("Status: " + status);
        System.out.println("Code: " + status.getCode());
        System.out.println("Message: " + status.getMessage());

        System.out.println("\n=== Operation Example ===");
        Operation op = Operation.PLUS;
        System.out.println("5 " + op.getSymbol() + " 3 = " + op.apply(5, 3));

        System.out.println("\n=== All Operations ===");
        for (Operation operation : Operation.values()) {
            System.out.println("10 " + operation.getSymbol() + " 2 = " + 
                             operation.apply(10, 2));
        }

        System.out.println("\n=== Demonstrating that constants are instances ===");
        // Each constant is actually an object instance
        System.out.println("EARTH instanceof Planet: " + (Planet.EARTH instanceof Planet));
        System.out.println("OK instanceof HttpStatus: " + (HttpStatus.OK instanceof HttpStatus));
        
        // Each instance has its own memory and state
        System.out.println("EARTH == MARS: " + (Planet.EARTH == Planet.MARS));
        System.out.println("EARTH == EARTH: " + (Planet.EARTH == Planet.EARTH));
    }
}```
    * example2
      * ```java
// Example 1: Simple enum without constructor
enum BasicColor {
    RED, GREEN, BLUE, YELLOW
    // Each constant is just a name, no additional data
}

// Example 2: Pizza sizes with price and diameter
enum PizzaSize {
    // Each constant calls the constructor with specific values
    SMALL("Small", 8, 12.99),
    MEDIUM("Medium", 12, 16.99),
    LARGE("Large", 16, 20.99),
    EXTRA_LARGE("Extra Large", 20, 24.99);

    // Instance variables - each enum constant has these
    private final String displayName;
    private final int diameterInches;
    private final double price;

    // Constructor - called when each constant is created
    PizzaSize(String displayName, int diameterInches, double price) {
        this.displayName = displayName;
        this.diameterInches = diameterInches;
        this.price = price;
    }

    // Getter methods
    public String getDisplayName() { return displayName; }
    public int getDiameterInches() { return diameterInches; }
    public double getPrice() { return price; }

    // Calculate area
    public double getAreaSquareInches() {
        double radius = diameterInches / 2.0;
        return Math.PI * radius * radius;
    }

    @Override
    public String toString() {
        return displayName + " (" + diameterInches + "\" - $" + price + ")";
    }
}

// Example 3: Employee roles with salary ranges and permissions
enum EmployeeRole {
    INTERN("Intern", 30000, 40000, false, false),
    DEVELOPER("Software Developer", 70000, 120000, true, false),
    SENIOR_DEVELOPER("Senior Developer", 100000, 150000, true, true),
    MANAGER("Manager", 90000, 140000, true, true),
    DIRECTOR("Director", 140000, 200000, true, true);

    private final String title;
    private final int minSalary;
    private final int maxSalary;
    private final boolean canAccessProduction;
    private final boolean canHireEmployees;

    // Constructor
    EmployeeRole(String title, int minSalary, int maxSalary, 
                 boolean canAccessProduction, boolean canHireEmployees) {
        this.title = title;
        this.minSalary = minSalary;
        this.maxSalary = maxSalary;
        this.canAccessProduction = canAccessProduction;
        this.canHireEmployees = canHireEmployees;
    }

    public String getTitle() { return title; }
    public int getMinSalary() { return minSalary; }
    public int getMaxSalary() { return maxSalary; }
    public boolean canAccessProduction() { return canAccessProduction; }
    public boolean canHireEmployees() { return canHireEmployees; }

    public String getSalaryRange() {
        return "$" + minSalary + " - $" + maxSalary;
    }
}

// Example 4: File types with extensions and descriptions
enum FileType {
    IMAGE("Image File", new String[]{"jpg", "png", "gif", "bmp"}, "photo.png"),
    DOCUMENT("Document", new String[]{"pdf", "doc", "docx", "txt"}, "document.png"),
    VIDEO("Video File", new String[]{"mp4", "avi", "mov", "wmv"}, "video.png"),
    AUDIO("Audio File", new String[]{"mp3", "wav", "flac", "m4a"}, "audio.png"),
    ARCHIVE("Archive", new String[]{"zip", "rar", "7z", "tar"}, "archive.png");

    private final String description;
    private final String[] extensions;
    private final String iconFileName;

    FileType(String description, String[] extensions, String iconFileName) {
        this.description = description;
        this.extensions = extensions.clone(); // Defensive copy
        this.iconFileName = iconFileName;
    }

    public String getDescription() { return description; }
    public String[] getExtensions() { return extensions.clone(); }
    public String getIconFileName() { return iconFileName; }

    // Check if a file extension belongs to this type
    public boolean hasExtension(String extension) {
        String lowerExt = extension.toLowerCase();
        for (String validExt : extensions) {
            if (validExt.equals(lowerExt)) {
                return true;
            }
        }
        return false;
    }

    // Static method to find file type by extension
    public static FileType getByExtension(String extension) {
        for (FileType type : FileType.values()) {
            if (type.hasExtension(extension)) {
                return type;
            }
        }
        return null; // Unknown file type
    }
}

// Demo class showing practical usage
public class EnumExamples {
    public static void main(String[] args) {
        System.out.println("=== Pizza Size Example ===");
        PizzaSize myOrder = PizzaSize.LARGE;
        System.out.println("I ordered: " + myOrder);
        System.out.println("Price: $" + myOrder.getPrice());
        System.out.println("Diameter: " + myOrder.getDiameterInches() + " inches");
        System.out.println("Area: " + String.format("%.1f", myOrder.getAreaSquareInches()) + " square inches");

        System.out.println("\n=== All Pizza Sizes ===");
        for (PizzaSize size : PizzaSize.values()) {
            System.out.println(size + " - Area: " + 
                String.format("%.1f", size.getAreaSquareInches()) + " sq in");
        }

        System.out.println("\n=== Employee Role Example ===");
        EmployeeRole myRole = EmployeeRole.SENIOR_DEVELOPER;
        System.out.println("My role: " + myRole.getTitle());
        System.out.println("Salary range: " + myRole.getSalaryRange());
        System.out.println("Can access production: " + myRole.canAccessProduction());
        System.out.println("Can hire employees: " + myRole.canHireEmployees());

        System.out.println("\n=== File Type Example ===");
        String fileName = "vacation.jpg";
        String extension = fileName.substring(fileName.lastIndexOf('.') + 1);
        
        FileType fileType = FileType.getByExtension(extension);
        if (fileType != null) {
            System.out.println("File: " + fileName);
            System.out.println("Type: " + fileType.getDescription());
            System.out.println("Icon: " + fileType.getIconFileName());
            System.out.print("Supported extensions: ");
            for (String ext : fileType.getExtensions()) {
                System.out.print(ext + " ");
            }
            System.out.println();
        }

        System.out.println("\n=== Key Point: Each constant is a unique instance ===");
        System.out.println("SMALL pizza price: $" + PizzaSize.SMALL.getPrice());
        System.out.println("LARGE pizza price: $" + PizzaSize.LARGE.getPrice());
        System.out.println("They're different objects with different data!");
        
        // Each constant is created once when the class is first loaded
        System.out.println("SMALL == SMALL: " + (PizzaSize.SMALL == PizzaSize.SMALL)); // true
        System.out.println("SMALL == LARGE: " + (PizzaSize.SMALL == PizzaSize.LARGE)); // false
    }
}```