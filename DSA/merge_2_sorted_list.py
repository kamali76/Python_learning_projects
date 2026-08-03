from typing import Optional

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

    def __str__(self):
        values = []
        current = self

        while current:
            values.append(str(current.val))
            current = current.next
        return " -> ".join(values)


class Solution:
    def mergeTwoLists(self, list1: Optional[ListNode], list2: Optional[ListNode]) -> Optional[ListNode]:
        if not list1:
            return list2
        if not list2:
            return list1
        if list1.val <= list2.val:
            list1.next = self.mergeTwoLists(list1.next, list2)
            return list1
        else:
            list2.next = self.mergeTwoLists(list1, list2.next)
            return list2

obj = Solution()
# declaring 1st listNode
list1 = ListNode(1)
list1.next = ListNode(2)
list1.next.next = ListNode(4)

# declaring 2nd listNode
list2 = ListNode(1)
list2.next = ListNode(3)
list2.next.next = ListNode(4)

result = obj.mergeTwoLists(list1, list2)

print(result)