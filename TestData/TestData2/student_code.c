
#include "student_code.h"
#include <string.h>
#include <stdlib.h>

String String__init(char* input_c_str) {
  String new_str;

  // Get size of the input string since we use it a few times throughout
  size_t length_of_string = strlen(input_c_str);

  // Set metadata associated with the string
  new_str.length = length_of_string;
  new_str.capacity = length_of_string + 1;

  // Copy over the data itself
  new_str.data = malloc(new_str.capacity);
  strncpy(new_str.data, input_c_str, new_str.capacity);

  // Return the string
  return new_str;
}

void String__delete(String* str) {
  free(str->data);
}

size_t String__length(const String* str) {
  return str->length;
}

size_t String__capacity(const String* str) {
  return str->capacity;
}

void String__reserve(String* str, size_t new_capacity) {
  if (new_capacity > str->capacity - 1) {
    char* new_data = malloc(new_capacity + 1);
    strncpy(new_data, str->data, str->length);
    memset(new_data + str->length, '\0', new_capacity + 1 - str->length);
    free(str->data);
    str->data = new_data;
    str->capacity = new_capacity + 1;
  }
}

void String__resize(String* str, size_t new_size, const char c) {
  if (new_size > str->capacity) {
    String__reserve(str, new_size);
  }
  
  if (new_size > str->length) {
    for (size_t i = str->length; i < new_size; i++) {
      str->data[i] = c;
    }
  } else if (new_size < str->length) {
    // Zero-fill the memory that was released
    memset(str->data + new_size, '\0', str->length - new_size + 1);
  }
  
  str->length = new_size;
  str->data[str->length] = '\0';
}

void String__clear(String* str) {
  str->length = 0;
  str->data[0] = '\0';
}

bool String__empty(String* str) {
  return str->length == 0;
}

char String__at(String* str, size_t index) {
  if (index < str->length) {
    return str->data[index];
  }
  return '\0';
}

char String__back(String* str) {
  if (str->length > 0) {
    return str->data[str->length - 1];
  }
  return '\0';
}

char String__front(String* str) {
  if (str->length > 0) {
    return str->data[0];
  }
  return '\0';
}

void String__append(String* str, const String* str_to_add) {
  size_t new_length = str->length + str_to_add->length;
  if (new_length + 1 > str->capacity) {
    String__reserve(str, new_length + 1);
  }
  strncpy(str->data + str->length, str_to_add->data, str_to_add->length);
  str->length = new_length;
  str->data[str->length] = '\0';
}

void String__push_back(String* str, const char char_to_add) {
  if (str->length + 2 > str->capacity) {
    String__reserve(str, str->capacity * 2 + 1);
  }
  str->data[str->length] = char_to_add;
  str->length++;
  str->data[str->length] = '\0';
}

void String__pop_back(String* str) {
  if (str->length > 0) {
    str->length--;
    str->data[str->length] = '\0';
  }
}

void String__insert(String* str, const String* str_to_insert, size_t index) {
  if (index > str->length) {
    index = str->length;
  }
  
  size_t new_length = str->length + str_to_insert->length;
  if (new_length + 1 > str->capacity) {
    String__reserve(str, new_length + 1);
  }
  
  // Shift characters after index to the right
  for (size_t i = str->length; i > index; i--) {
    str->data[i + str_to_insert->length - 1] = str->data[i - 1];
  }
  
  // Copy the new string into position
  strncpy(str->data + index, str_to_insert->data, str_to_insert->length);
  str->length = new_length;
  str->data[str->length] = '\0';
}

void String__erase(String* str, size_t pos, size_t len) {
  if (pos >= str->length) {
    return;
  }
  
  if (pos + len > str->length) {
    len = str->length - pos;
  }
  
  // Shift characters left
  for (size_t i = pos; i < str->length - len; i++) {
    str->data[i] = str->data[i + len];
  }
  
  str->length -= len;
  str->data[str->length] = '\0';
}

void String__replace(String* str, size_t pos, size_t len, const String* str_to_replace_with) {
  if (pos >= str->length) {
    return;
  }
  
  if (pos + len > str->length) {
    len = str->length - pos;
  }
  
  size_t new_length = str->length - len + str_to_replace_with->length;
  
  if (new_length + 1 > str->capacity) {
    String__reserve(str, new_length + 1);
  }
  
  // If replacement is larger, shift right; if smaller, shift left
  if (str_to_replace_with->length > len) {
    for (size_t i = str->length; i > pos + len; i--) {
      str->data[i + str_to_replace_with->length - len - 1] = str->data[i - 1];
    }
  } else if (str_to_replace_with->length < len) {
    for (size_t i = pos + str_to_replace_with->length; i < str->length - len + str_to_replace_with->length; i++) {
      str->data[i] = str->data[i + len - str_to_replace_with->length];
    }
  }
  
  // Copy the replacement string
  strncpy(str->data + pos, str_to_replace_with->data, str_to_replace_with->length);
  str->length = new_length;
  str->data[str->length] = '\0';
}

void String__swap(String* str1, String* str2) {
  String temp = *str1;
  *str1 = *str2;
  *str2 = temp;
}
