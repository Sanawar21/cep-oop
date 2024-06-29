def decorator(func):
    def wrapper(*args, **kwargs):
        some_data = {
            "name": "Sanawar",
            "age": 19,
        }
        func(*args, **kwargs)

    return wrapper


@decorator
def func():
    print("I use some_data")
    print(some_data)


func()
