class CustomerException(BaseException):
    pass


class CustomerAddException(CustomerException):
    pass


class CustomerDeleteException(CustomerException):
    pass
