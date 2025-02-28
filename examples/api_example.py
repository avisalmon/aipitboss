"""
Example usage of the AIPitBoss package.

This script demonstrates how to use the APIConnect class
to interact with an API.
"""

from aipitboss.api_connect import APIConnect


def main():
    """
    Main function demonstrating API Connect usage.
    """
    # Create an API connection
    # Replace with your actual API key and base URL
    api = APIConnect(
        api_key="your_api_key_here",
        base_url="https://api.example.com/v1",
        timeout=60  # Longer timeout for large responses
    )
    
    try:
        # Example GET request
        print("Making GET request...")
        response = api.get("/users", params={"limit": 10})
        print(f"GET response: {response}")
        
        # Example POST request
        print("\nMaking POST request...")
        create_response = api.post(
            "/users",
            json_data={
                "name": "John Doe",
                "email": "john.doe@example.com"
            }
        )
        print(f"POST response: {create_response}")
        
        # Example PUT request to update
        user_id = create_response.get("id", "123")
        print(f"\nMaking PUT request for user {user_id}...")
        update_response = api.put(
            f"/users/{user_id}",
            json_data={
                "name": "John Doe Updated",
                "email": "john.updated@example.com"
            }
        )
        print(f"PUT response: {update_response}")
        
        # Example DELETE request
        print(f"\nMaking DELETE request for user {user_id}...")
        delete_response = api.delete(f"/users/{user_id}")
        print(f"DELETE response: {delete_response}")
        
    except Exception as e:
        print(f"Error occurred: {e}")


if __name__ == "__main__":
    main()
