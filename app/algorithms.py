def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)

def merge(left, right):
    result = []
    while left and right:
        if left[0]['price'] < right[0]['price']:
            result.append(left.pop(0))
        else:
            result.append(right.pop(0))
    return result + left + right
