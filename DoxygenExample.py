## @package Package If it existed it would have been documented here.

## **Figure class description.**
# *This class creates Figures.*
class Figure:

    ## @var Class variable.
    ##  Class variables are documented here
    classVar = -1

    ## Figure constructor.
    #  @param name The name of the Figure.
    #  @param sides The number of sides the Figure has.
    #  @return The object.
    #  @warning This is important!
    #  @attention This is less important.
    #  @note This is almost not important.
    #  @see setName() setSides() showFigure()
    def __init__(self, name, sides):
        ## This is the variable used to set the Figure name.
        self.name = name    
        ## This is the variable used to se the Figure side number.
        self.sides = sides  
    
    ##  Name setter.
    #    @param name The name of the Figure.
    
    def setName(self, name):
        self.name = name

    ## Side setter.
    #  @param sides The number of sides the Figure has.
    def setSides(self, sides):
        self.sides = sides
    
    ## Show the figure
    def showFigure(self):
        print("The figure: " + self.name + " has: ", self.sides, " sides.")

## Example code, Figure creation
f1 = Figure("Rectangle", 4)
f1.showFigure()
f1.setName("Triangle")
f1.setSides(3)
f1.showFigure()