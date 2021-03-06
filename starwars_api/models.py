from starwars_api.client import SWAPIClient
from starwars_api.exceptions import SWAPIClientError

api_client = SWAPIClient()


class BaseModel(object):

    def __init__(self, json_data):
        """
        Dynamically assign all attributes in `json_data` as instance
        attributes of the Model.
        """
        self.data = json_data
        
        for keys,values in json_data.items():
            setattr(self, keys, values)
        
    @classmethod
    def get(cls, resource_id):
        """
        Returns an object of current Model requesting data to SWAPI using
        the api_client.
        """
        method=getattr(api_client,"get_"+cls.RESOURCE_NAME)
        result=method(resource_id)
		
        return BaseModel(result)

    @classmethod
    def all(cls):
        """
        Returns an iterable QuerySet of current Model. The QuerySet will be
        later in charge of performing requests to SWAPI for each of the
        pages while looping.
        """
        name_of_child = cls.RESOURCE_NAME.title()
        result = eval(name_of_child+"QuerySet")
        
        return result()
        

class People(BaseModel):
    """Representing a single person"""
    RESOURCE_NAME = 'people'

    def __init__(self, json_data):
        super(People, self).__init__(json_data)

    def __repr__(self):
        return 'Person: {0}'.format(self.name)


class Films(BaseModel):
    RESOURCE_NAME = 'films'

    def __init__(self, json_data):
        super(Films, self).__init__(json_data)

    def __repr__(self):
        return 'Film: {0}'.format(self.title)


class BaseQuerySet(object):

    def __init__(self):
        self.index = 0
        self.max_iterations=0
        self.get_data = getattr(api_client, 'get_' + self.RESOURCE_NAME)
        self.page = 1

    def __iter__(self):
        return self

    def __next__(self):
        """
        Must handle requests to next pages in SWAPI when objects in the current
        page were all consumed.
        """
        data =  self.get_data("page="+str(self.page))
        
        if self.max_iterations != data["count"]:
            obj = data["results"][self.index]
            self.max_iterations += 1
            if self.index < len(data["results"]) - 1:
                self.index += 1
            else:
                self.index = 0
            result = eval(self.RESOURCE_NAME.title())
            return result(obj)
        else:
            raise StopIteration()
    next = __next__

    def count(self):
        """
        Returns the total count of objects of current model.
        If the counter is not persisted as a QuerySet instance attr,
        a new request is performed to the API in order to get it.
        """
        result = self.get_data()
        
        return result["count"]
        

class PeopleQuerySet(BaseQuerySet):
    RESOURCE_NAME = 'people'

    def __init__(self):
        super(PeopleQuerySet, self).__init__()

    def __repr__(self):
        return 'PeopleQuerySet: {0} objects'.format(str(len(self.objects)))


class FilmsQuerySet(BaseQuerySet):
    RESOURCE_NAME = 'films'

    def __init__(self):
        super(FilmsQuerySet, self).__init__()

    def __repr__(self):
        return 'FilmsQuerySet: {0} objects'.format(str(len(self.objects)))
