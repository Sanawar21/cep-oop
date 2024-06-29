def decorator(func):
    def wrapper(*args, **kwargs):
        some_data = {
            "name": "Sanawar",
            "age": 19,
        }
        func(*args, **kwargs, some_data=some_data)

    return wrapper


@decorator
def func(some_data):
    print("I use some_data")
    print(some_data)


func()
