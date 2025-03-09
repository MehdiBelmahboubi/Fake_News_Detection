export const getAllNews = async () => {
    try {
        const response = await fetch('/api/News/getAll', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });
        const news = await response.json();
        return news;
    } catch (error) {
        console.error('Error fetching news:', error);
        throw error;
    }
};

export const checkNews = async (query: string) => {
    try {
        const response = await fetch(`/api/News/checkNews?query=${encodeURIComponent(query)}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const news = await response.json();
        return news;
    } catch (error) {
        console.error('Error fetching news:', error);
        throw error;
    }
};

export const checkPdfNews = async (file: File) => {
    try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('/api/News/checkPdf', {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const result = await response.json();
        return result;
    } catch (error) {
        console.error('Error checking PDF news:', error);
        throw error;
    }
};