from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255)
     
    def __str__(self):
        return self.name + ' - ' + str(self.id)
           

class Menu(models.Model):
    name = models.CharField(max_length=255)
    img = models.ImageField(upload_to='menu/')
    desc = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-id']

class Contact(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name