with open("example.txt") as file:
    line_count = sum(1 for line in file)
print(f"Line count: {line_count}")
